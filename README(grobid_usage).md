## Install Grobid

1. Requires java
2. Follow: https://grobid.readthedocs.io/en/latest/Install-Grobid/

## Run Grobid server (Terminal 1)
1. Go to grobid folder
2. Run: `./gradlew run`

## Install Grobid client
1. `git clone https://github.com/kermitt2/grobid_client_python`
2. `cd grobid_client_python`
3. `python3 setup.py install`

## Run Grobid client (Terminal 2)
1. Go to grobid_client_python folder
2. Run: `grobid_client --input ~/tmp/in2 --output ~/tmp/out processFulltextDocument`
