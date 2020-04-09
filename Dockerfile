FROM kbase/sdkbase2:python
MAINTAINER KBase Developer

# Install pip dependencies
RUN pip install -U --upgrade pip cerberus==1.3 Template-Toolkit-Python

COPY ./ /kb/module

WORKDIR /kb/module

RUN mkdir -p /kb/module/work \
    && chmod -R a+rw /kb/module \
    && make all

ENV TEMPLATE_DIR /kb/module/kbase_report_templates
ENV APP_DIR /kb/module

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
