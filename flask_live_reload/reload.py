import os
from flask import Flask


class LiveReload:

    def __init__(self, app: Flask):
        self.app = app

        self._create_reload_route()
        self._register_template_helper()

    def _create_reload_route(self):

        @self.app.route("/__reload_check")
        def reload_check():

            files = []

            for root, dirs, filenames in os.walk("."):

                # Ignore virtual environments
                dirs[:] = [
                    d for d in dirs
                    if d not in ("venv", ".venv", "__pycache__")
                ]

                for filename in filenames:

                    if filename.endswith((
                        ".py",
                        ".html",
                        ".css",
                        ".js"
                    )):

                        path = os.path.join(root, filename)

                        try:
                            files.append(
                                str(os.path.getmtime(path))
                            )
                        except OSError:
                            pass

            return "|".join(files)

    def _register_template_helper(self):

        @self.app.context_processor
        def inject_live_reload():

            return {
                "live_reload_script": self.script()
            }

    def script(self):

        return """
<script>
let lastVersion = null;

async function checkForChanges() {

    try {

        const response = await fetch(
            "/__reload_check",
            {
                cache: "no-store"
            }
        );

        const currentVersion = await response.text();

        if (lastVersion === null) {

            lastVersion = currentVersion;
            return;
        }

        if (currentVersion !== lastVersion) {

            location.reload();

        }

    } catch (error) {

        console.log("Live reload check failed");

    }
}

setInterval(checkForChanges, 1000);
</script>
"""