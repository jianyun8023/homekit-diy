FROM alpine:3.12
WORKDIR /app
ENV MIIO_HOST 192.168.1.1
ENV MIIO_TOKEN bd5331094c79167c30118549fd53137d
RUN apk add --no-cache \
     git \
     gcc \
     curl \
     linux-headers \
     musl-dev \
     libffi-dev \
     openssl-dev \
     python3 \
     python3-dev \
     py3-cffi && \     
     curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
     python3 get-pip.py && rm -f get-pip.py && \
     pip install python-miio HAP-python[QRCode] && \
     apk del git gcc linux-headers musl-dev python3-dev curl
COPY mifan.py .
ENTRYPOINT [ "python3","mifan.py" ]
