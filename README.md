Overview

This project has 2 logical transformers:
1. str_logical_transformer : Parses code as a string and transforms it logically (replaces keywords listed below while ensuring the output remains the same)
2. ast_logical_transformer : Uses Python's Abstract Syntax Tree (via the ast module) to transform code logically (replaces keywords listed below while ensuring the output remains the same)

Replaced Keywords:

1. elif
2. else
3. in
4. and
5. or
6. not
