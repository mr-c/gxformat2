#!/bin/bash

set -x
set -e

PROJECT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SKIP_JAVA=${SKIP_JAVA:-0}
DIST_DIRECTORY="${PROJECT_DIRECTORY}/dist/schema"
rm -rf "${DIST_DIRECTORY}"
mkdir -p "${DIST_DIRECTORY}"
cp schema/*png "${DIST_DIRECTORY}"

# Requires schema-salad-doc that recognizes --brandstyle and --brandinverse
for schema in "v19_09";
do
    cd schema/"$schema";
    python_schema_name=${schema//./_}
    schema-salad-tool --codegen python workflow.yml > "${PROJECT_DIRECTORY}/gxformat2/schema/${python_schema_name}.py"

    out="${DIST_DIRECTORY}/${schema}.html"
    schema-salad-doc \
        --brandstyle '<link rel="stylesheet" href="https://jamestaylor.org/galaxy-bootstrap/galaxy_bootstrap.css">' \
        --brandinverse \
        --brand '<img src="icon.png" />' \
        --brandlink '' \
        --only "https://galaxyproject.org/gxformat2/${schema}#WorkflowDoc" \
        --only "https://galaxyproject.org/gxformat2/${schema}#GalaxyWorkflow" \
        workflow.yml > "$out"

    if [ $SKIP_JAVA -eq 0 ]; then
        java_package="${PROJECT_DIRECTORY}/java"
        schema-salad-tool \
            --codegen java \
            --codegen-target "$java_package" \
            --codegen-examples examples \
            workflow.yml
        cd "$java_package"
        mvn test
        mvn javadoc:javadoc
        cd "${PROJECT_DIRECTORY}"
    fi
done
