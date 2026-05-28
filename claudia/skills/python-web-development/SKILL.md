---
name: python-web-development
description: >
  Patterns Claude tends to miss when building Streamlit + SQLAlchemy apps: session lifecycle
  mistakes, missing @st.cache_resource when reviewing or refactoring existing code, hardcoded
  credentials in fixes, and unsafe multi-page DB state. Activate proactively when the user is
  building, reviewing, or fixing a Streamlit app that uses SQLAlchemy — even if they don't say
  "best practices". Trigger on: "session state", "database connection", "streamlit + sqlalchemy",
  "scoped_session", any Streamlit file that opens a DB session, any multi-page app structure question.
---

# Streamlit + SQLAlchemy — Only What Claude Tends to Miss

The benchmark for this skill: eval 1 (write database.py from scratch) shows no gap — Claude already gets it right. The gaps are in **code review, architecture questions, and session state misuse**.

## Session Lifecycle — The #1 Priority

Every Streamlit rerun executes the script top-to-bottom. The most destructive pattern is storing a SQLAlchemy session in `st.session_state`: Streamlit persists it across reruns, keeping the transaction open, accumulating stale identity-map entries, and eventually exhausting the connection pool or returning stale data.

```python
# Wrong — session survives reruns, holds stale data, leaks connections
if "db_session" not in st.session_state:
    st.session_state["db_session"] = SessionLocal()
session = st.session_state["db_session"]  # stale after first rerun

# Correct — session opens and closes in one interaction
def get_users() -> list[User]:
    Session = get_session_factory()
    with Session() as session:          # closed automatically; no leak
        return session.scalars(select(User)).all()
```

One context manager per user action, not per page load. `st.session_state` is for scalars only: user IDs, form values, selected row keys — never ORM objects or sessions.

## `@st.cache_resource` — Even When Reviewing Existing Code

Claude applies `@st.cache_resource` naturally when writing a new `database.py`. The gap is when **reviewing or refactoring** code that uses `scoped_session`, `sessionmaker` at module level, or a custom `get_db()` without caching — Claude tends to preserve the existing pattern instead of flagging it.

When you see any of these, flag and fix:

```python
# Patterns to replace — all create a new pool on every Streamlit rerun
engine = create_engine(DATABASE_URL)                     # module-level
Session = scoped_session(sessionmaker(bind=engine))      # scoped_session is wrong here

# Correct — pool created once per process
@st.cache_resource
def get_engine():
    return create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)

@st.cache_resource
def get_session_factory():
    return sessionmaker(bind=get_engine(), expire_on_commit=False)
```

`scoped_session` is a thread-local registry, not a cache — it doesn't survive Streamlit's per-rerun model. `@st.cache_resource` is the correct Streamlit idiom.

`expire_on_commit=False` matters in Streamlit: without it, ORM attributes raise `DetachedInstanceError` when accessed after the session context manager closes (which happens before widget rendering).

## Security in Code Reviews

When reviewing or fixing existing code, Claude tends to fix the logic bugs while leaving the credentials in place. Always flag both:

- **Hardcoded connection strings** — replace with `os.environ["DATABASE_URL"]` or `st.secrets["DATABASE_URL"]`. A hardcoded string in a fix is still a vulnerability.
- **f-string SQL** — replace with `text("... :param")` + bound dict. ORM queries are safe by default; only `session.execute(text(...))` needs this.
- **Raw exceptions in the UI** — `st.error(str(e))` leaks schema names, table names, and column names. Always catch and show a generic message; log the real error.

## Multi-Page App Structure

When designing architecture, the temptation is `scoped_session` for thread safety. In Streamlit this is wrong — use `@st.cache_resource` for the engine/factory, and fresh context-manager sessions per interaction.

```
myapp/
├── database.py       # @st.cache_resource for engine + factory — imported by all pages
├── models/           # ORM models, no Streamlit imports
├── repositories/     # all DB access via context managers, no Streamlit imports
├── pages/            # thin Streamlit pages; call repositories, never open sessions directly
└── auth.py           # require_login() guard using st.session_state["user_id"] (int only)
```

`st.session_state` holds only the `user_id` int. Pages fetch objects fresh from the DB on each rerun using that ID — never store ORM objects in session state.

## Quick Reference

| Situation | Pattern |
|-----------|---------|
| Session per action | `with Session() as s:` — never stored in `st.session_state` |
| Engine / factory setup | `@st.cache_resource` on `get_engine()` and `get_session_factory()` |
| Reviewing code with `scoped_session` | Replace with `@st.cache_resource` |
| Post-commit attribute access | `expire_on_commit=False` on sessionmaker |
| Raw SQL | `session.execute(text("... :p"), {"p": val})` |
| Credentials in a fix | Flag and replace with env var / st.secrets |
| Error display | Generic `st.error()` + `logger.exception()` internally |
