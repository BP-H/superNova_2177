def test_package_import():
    from introspection import introspection_pipeline
    assert hasattr(introspection_pipeline, "run_full_audit")
