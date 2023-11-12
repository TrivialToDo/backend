FROM condaforge/mambaforge

ENV DEPLOY 1

WORKDIR /opt/tmp

COPY . .

RUN apt-get update && \
    apt-get install -y jq && \
    rm -rf /var/lib/apt/lists/*

RUN mamba create -n py310 python=3.10 && \
    echo "conda activate py310" >> ~/.bashrc && \
    /bin/bash -c "source ~/.bashrc" && \
    mamba install -n py310 -c conda-forge faiss-cpu && \
    mamba install -c conda-forge uwsgi && \
    /bin/bash -c "conda init bash" && \
    pip install -r requirements.txt

EXPOSE 6666

CMD ["sh", "start.sh"]
