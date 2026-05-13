# nf-test for SAMTOOLS_INDEX (baseline, no skill)

Here's a complete nf-test file for the `SAMTOOLS_INDEX` process.

## Test file: `tests/modules/samtools/index/main.nf.test`

```groovy
nextflow_process {

    name "Test SAMTOOLS_INDEX"
    script "modules/samtools/index/main.nf"
    process "SAMTOOLS_INDEX"

    test("Should index a sorted BAM file and produce a .bai output") {

        when {
            process {
                """
                input[0] = [
                    [ id: 'test_sample', single_end: false ],
                    file("${projectDir}/tests/data/test_sorted.bam")
                ]
                """
            }
        }

        then {
            assert process.success

            with(process.out.bai) {
                assert size() == 1
                assert get(0).get(1) ==~ /.*\.bai$/
            }

            assert process.out.versions
        }
    }

    test("Should produce snapshot-matching output for a sorted BAM file") {

        when {
            process {
                """
                input[0] = [
                    [ id: 'test_sample', single_end: false ],
                    file("${projectDir}/tests/data/test_sorted.bam")
                ]
                """
            }
        }

        then {
            assert process.success

            snapshot(
                process.out.bai,
                process.out.versions
            ).match()
        }
    }
}
```

## Design notes

- The `when { process { ... } }` block provides inputs using the `input[0]` notation.
- The meta map `[ id: 'test_sample', single_end: false ]` matches nf-core conventions.
- Test 1 checks the `.bai` extension using a regex match `==~ /.*\.bai$/`.
- Test 2 uses `snapshot()` to capture the full output for reproducibility checking.
- Both tests reference `${projectDir}` so paths stay portable across environments.