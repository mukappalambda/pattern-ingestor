# Pattern Ingestor

A tool for improving my english.

To install the dependencies, run:

```bash=
pip install -r requirements.txt
```

Go to [News API](https://newsapi.org/) to get the API key.

Create a file called `app.json` with the content similar as below:

```json=
{
  "API_KEY": "MY_API_KEY"
}
```

Now we can execute the `main.py` with a query as the first argument:

```bash=
python main.py 'Russian invasion of Ukraine'
```

Issues:

- [ ] Hard-coded single source (i.e. CNN news) and parsing logic.
- [ ] There are occasionally some unreasonable sentences.
