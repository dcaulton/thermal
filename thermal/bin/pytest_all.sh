#! /bin/sh

cd ~/thermal
py.test --cov-report= \
        --cov-config ./.coveragerc \
        --cov=admin admin
py.test --cov-report= \
        --cov-config ./.coveragerc \
        --cov-append \
        --cov=analysis analysis
py.test --cov-report= \
        --cov-config ./.coveragerc \
        --cov-append \
        --cov=calibration calibration
py.test --cov-report= \
        --cov-config ./.coveragerc \
        --cov-append \
        --cov=camera camera
py.test --cov-report= \
        --cov-config ./.coveragerc \
        --cov-append \
        --cov=merging merging
py.test --cov-report= \
        --cov-config ./.coveragerc \
        --cov-append \
        --cov=picture picture
py.test --cov-report term-missing \
        --cov-config ./.coveragerc \
        --cov-append \
        --cov=thermal thermal

coverage report -m > coverage_report
