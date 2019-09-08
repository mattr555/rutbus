# [rutb.us](https://rutb.us/): plaintext Rutgers bus predictions

Usage: `curl https://rutb.us/<route_or_stop>`

## Demo

[![asciicast](https://asciinema.org/a/oLY2y68wFNxWx1AplAArY13PJ.svg)](https://asciinema.org/a/oLY2y68wFNxWx1AplAArY13PJ)

## Bash Function

Even simpler access to the data! Add to your `.bashrc`, `.zshrc`, etc.

```bash
rutbus()
{
    curl "https://rutb.us/${1}"
}
```

## Development

This project is heavily inspired by [wttr.in](http://wttr.in/).

It was built using AWS Lambda, hooked up to AWS API Gateway. The custom domain is managed by CloudFront and Route 53. Logging is automatically done by CloudWatch. It was fun to play with the tools that will eventually replace my job!

This project is most useful for Rutgers New Brunswick and it's multifaceted, complex bus schedule, but it could work for any transit service that uses the Transloc API to report predictions. Just swap out the agency ID and the routes and stops CSVs.

Those CSV files were originally generated with a set of scripts that call the `routes` and `stops` endpoints of the Transloc API. Their implementation is left as an exercise for the reader (_i.e._ I lost them).