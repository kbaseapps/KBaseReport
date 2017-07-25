FROM kbase/kbase:sdkbase.latest
MAINTAINER KBase Developer
# -----------------------------------------

# Insert apt-get instructions here to install
# any required dependencies for your module.

# RUN apt-get update
RUN cpanm -i Config::IniFiles && \
    cpanm -i UUID::Random && \
    cpanm -i HTML::SimpleLinkExtor && \
    cpanm -i WWW::Mechanize --force && \
    cpanm -i MIME::Base64 && \
    apt-get -y install nano

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work && \
    chmod -R 777 /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
