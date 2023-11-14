from typing import Dict, Any

from dbt.config.renderer import BaseRenderer, Keypath


# This class renders dictionaries derived from "schema" yaml files.
# It calls Jinja on strings (in deep_map_render), except for certain
# keys which are skipped because they need to be rendered later
# (tests and description). Test configs are rendered in the
# generic test builder code, but skips the keyword args. The test
# keyword args are rendered to capture refs in render_test_update.
# Keyword args are finally rendered at compilation time.
# Descriptions are not rendered until 'process_docs'.
class SchemaYamlRenderer(BaseRenderer):
    def __init__(self, context: Dict[str, Any], key: str) -> None:
        super().__init__(context)
        self.key = key

    @property
    def name(self):
        return "Rendering yaml"

    def _is_norender_key(self, keypath: Keypath) -> bool:
        """
        models:
            - name: blah
              description: blah
              data_tests: ...
              columns:
                - name:
                  description: blah
                  data_tests: ...

        Return True if it's data_tests or description - those aren't rendered now
        because they're rendered later in parse_generic_tests or process_docs.
        """
        # top level descriptions and tests
        if len(keypath) >= 1 and keypath[0] in ("data_tests", "description"):
            return True

        # columns descriptions and tests
        if len(keypath) == 2 and keypath[1] in ("data_tests", "description"):
            return True

        # versions
        if len(keypath) == 5 and keypath[4] == "description":
            return True

        if (
            len(keypath) >= 3
            and keypath[0] in ("columns", "dimensions", "measures", "entities")
            and keypath[2] in ("data_tests", "description")
        ):
            return True

        return False

    # don't render descriptions or test keyword arguments
    def should_render_keypath(self, keypath: Keypath) -> bool:
        if len(keypath) < 1:
            return True

        if self.key == "sources":
            if keypath[0] == "description":
                return False
            if keypath[0] == "tables":
                if self._is_norender_key(keypath[2:]):
                    return False
        elif self.key == "macros":
            if keypath[0] == "arguments":
                if self._is_norender_key(keypath[1:]):
                    return False
            elif self._is_norender_key(keypath[0:]):
                return False
        elif self.key == "metrics":
            # This ensures all key paths that end in 'filter' for a metric are skipped
            if keypath[-1] == "filter":
                return False
            elif self._is_norender_key(keypath[0:]):
                return False
        elif self.key == "saved_queries":
            if keypath[0] == "query_params" and len(keypath) > 1 and keypath[1] == "where":
                return False
            elif self._is_norender_key(keypath[0:]):
                return False
        else:  # models, seeds, snapshots, analyses
            if self._is_norender_key(keypath[0:]):
                return False
        return True
