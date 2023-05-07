# igv-flask

Flask webserver for rendering [igv.js](https://github.com/igvteam/igv.js).

It is available through `pip` with the following command:

```
pip install igv-flask
```

## How to start the webserver

In order to start the Flask webserver and rendering `igv.js` over an input fasta file, open your terminal and run the following command:

```
igv --host "0.0.0.0" --port 5000 --input ~/myfasta.fna --index ~/myfasta.fai
```

Run `igv --help` for a complite list of available options.
