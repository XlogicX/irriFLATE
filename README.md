# irriFLATE
the Impractically Redundant Redundant Interactive DEFLATE crafting tool #

usage: irriFLATE [-h] [--errors] [--colors]

optional arguments:<br>
  -h, --help  show this help message and exit<br>
  --errors    Allow Huffman table error conditions<br>
  --colors    Color code similar to infgen fork<br>

## Descirption
An interactive tool that allows you to craft compressed data (loosely) based on RFC1951. This tool allows for multiblock compressed data of stored, fixed, and dynamic modes. Dynamic mode being the most complex; of which you get to manually specify each field (counts, code length code table, symbol table, etc...). It is stated that this 'loosely' follows RFC1951 because though you can craft data that an INFLATEr should be able to parse, you can create data that no DEFLATE tool would craft. You can also create error conditions as well. You can craft custom 'huffman' (nonprefix) tables for all kinds of designer compression scenarios.

## Usage Screenshot(s):
![alt tag](https://github.com/XlogicX/irriFLATE/blob/main/irriflate01.png?raw=true)

## Examples
Long Nothing:<br>
edfd013cd7f8ffc7013c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1787cbfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fbfd7ebfdfeff7fb7d3c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1787c1f8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f17c3e9f8fc7e3f1783c1e8fc7e3f1783c1e8fc7e3f1783c1e8fc71f

invalid deflate data -- code lengths code is incomplete<br>
05c0ffffffffffff7fe29fb8060201

invalid deflate data -- code lengths code is oversubscribed<br>
05c025499224499224

invalid deflate data -- literal/length code is incomplete<br>
05c049922449926cdbfffffffff77ddff77ddff77ddff77ddff77ddff77ddff77ddff77ddff77ddff77ddff7ffffff4100

distance too far back (6/3)<br>
8b888c029200

ASCII printable compressed data:<br>
5 Ir$IPffffffffffffffffffffffffnnnnnnffffffnnnnffffnfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffnnnfffffffffffnnfVFu
