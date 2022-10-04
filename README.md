# irriFLATE
the Impractically Redundant Redundant Interactive DEFLATE crafting tool

usage: irriFLATE [-h] [--errors] [--colors]

optional arguments:<br>
  -h, --help  show this help message and exit<br>
  --errors    Allow Huffman table error conditions<br>
  --colors    Color code similar to infgen fork<br>

## Descirption
An interactive tool that allows you to craft compressed data (loosely) based on RFC1951. This tool allows for multiblock compressed data of stored, fixed, and dynamic modes. Dynamic mode being the most complex; of which you get to manually specify each field (counts, code length code table, symbol table, etc...). It is stated that this 'loosely' follows RFC1951 because though you can craft data that an INFLATEr should be able to parse, you can create data that no DEFLATE tool would craft. You can also create error conditions as well. You can craft custom 'huffman' (nonprefix) tables for all kinds of designer compression scenarios.

Note that the output is ASCII-Hex, as it is a binary format and this is a good representation of binary data

In Fixed and Dynaimic Huffman modes, you can enter length-distance pairs in the format of l,d. So Length of 3 and distance of 4 could be written 3,4. You can also enter the direct binary of the token from the huffman table if that's your thing.

Speaking of the symbol table, you can enter the command 'tables' at the Token prompt to see the available tokens and their bit patterns

## Usage Screenshot(s):
### Fixed Mode
![alt tag](https://github.com/XlogicX/irriFLATE/blob/main/irriflate01.png?raw=true)

### Stored Mode
![alt tag](https://github.com/XlogicX/irriFLATE/blob/main/irriflate02.png?raw=true)

### Dynamic Mode
![alt tag](https://github.com/XlogicX/irriFLATE/blob/main/dynamic.png?raw=true)
### Decompressing that result using phpcli
![alt tag](https://github.com/XlogicX/irriFLATE/blob/main/php.png?raw=true)

## Examples
Long Nothing (Single Block Dynamic Mode):<br>
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

![alt tag](https://github.com/XlogicX/irriFLATE/blob/main/cyberchef.png?raw=true)
