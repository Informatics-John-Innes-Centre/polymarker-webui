FROM debian:13.3

ENV DEBIAN_FRONTEND=noninteractive
# default packages 
RUN apt-get update && apt-get install -y wget git vim ca-certificates less which locales-all

# conda + bioinformatics tools
RUN mkdir -p /opt && cd /opt && \
    RELEASE="Miniforge3-Linux-x86_64.sh" && \
    wget "https://github.com/conda-forge/miniforge/releases/latest/download/${RELEASE}" && \
    bash $RELEASE -b -p /opt/miniforge3 && \
    rm -f $RELEASE && rm -f /opt/miniforge3/.condarc && \
    export PATH=/opt/miniforge3/condabin:$PATH && \
    conda config --add channels conda-forge && \
    conda config --add channels bioconda && \
    conda config --set channel_alias "https://repo.prefix.dev" && \
    conda install -y mamba
ENV PATH=/opt/software/bin:/opt/miniforge3/condabin:$PATH
RUN mamba create -qy -p /opt/software blast=2.16.0 primer3=2.6.1 samtools=1.21
RUN cd /tmp && wget https://mafft.cbrc.jp/alignment/software/mafft_7.526-1_amd64.deb -O mafft.deb && apt-get install -y ./mafft.deb

# ruby
ENV RBENV_ROOT=/opt/rbenv
ENV PATH=$RBENV_ROOT/bin:$RBENV_ROOT/shims:$PATH
RUN apt-get install build-essential zlib1g-dev liblzma-dev -y && \
    git clone https://github.com/sstephenson/rbenv.git $RBENV_ROOT && \
    git clone https://github.com/sstephenson/ruby-build.git $RBENV_ROOT/plugins/ruby-build && \
    rbenv install 3.0.7
RUN apt-get install -y libncurses-dev libbz2-dev && \
    rbenv global 3.0.7 && \
    gem install rake:13.2.1 sorted_set:1.0.3 bio-polymarker:1.3.3

# polymarker-webui
RUN wget -qO- https://astral.sh/uv/install.sh | sh
ENV PATH=/root/.local/bin/:$PATH
VOLUME /genomes
VOLUME /genome-descriptions
VOLUME /app/instance
WORKDIR /app
COPY pmwui ./pmwui
COPY pyproject.toml .
COPY uv.lock .
COPY .python-version .
RUN apt-get install -y libmariadb-dev && uv sync --no-dev
CMD ["uv", "run", "--no-sync", "gunicorn", "--log-level", "debug", "-w", "1", "--timeout", "600", "-b", "0.0.0.0:5000", "pmwui:create_app()"]
