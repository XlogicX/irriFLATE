# irriFLATE
the Impractically Redundant Redundant Interactive DEFLATE crafting tool

usage: irriFLATE [-h] [--errors] [--colors] [--gzip] [--png] [--file FILE] [--recipe RECIPE]

options:<br>
  -h, --help       show this help message and exit<br>
  --errors         Allow Huffman table error conditions<br>
  --colors         Color code similar to infgen fork<br>
  --gzip           Add gzip header nonsense<br>
  --png            Craft a fucked up image<br>
  --file FILE      An uncompressed version of the data provided for AdlerCRC32 calculation<br>
  --recipe RECIPE  Recipe of instructions in non-interactive fassion...irrFlate?<br>

## Descirption
An interactive tool that allows you to craft compressed data (loosely) based on RFC1951. This tool allows for multiblock compressed data of stored, fixed, and dynamic modes. Dynamic mode being the most complex; of which you get to manually specify each field (counts, code length code table, symbol table, etc...). It is stated that this 'loosely' follows RFC1951 because though you can craft data that an INFLATEr should be able to parse, you can create data that no DEFLATE tool would craft. You can also create error conditions as well. You can craft custom 'huffman' (nonprefix) tables for all kinds of designer compression scenarios.

Note that the output is ASCII-Hex, as it is a binary format and this is a good representation of binary data

In Fixed and Dynaimic Huffman modes, you can enter length-distance pairs in the format of l,d. So Length of 3 and distance of 4 could be written 3,4. You can also enter the direct binary of the token from the huffman table if that's your thing.

Speaking of the symbol table, you can enter the command 'tables' at the Token prompt to see the available tokens and their bit patterns

## WUT?
"I read the description, but I still have no idea how to actually use this tool." For now, the short answer, is that you kind of need to understand a bit of the RFCs involved to get the most out of this script. The level of hackery involved in this tool is similar to writing your own compression by hand with pen and paper. This tool just makes it so you don't have to deal with the tedious 1's and 0's, and it guides you from each logical field in order. Ideally more verbose documentation will follow, but it would likely be more text than RFC1951! You can look to the recipes for known good inputs.

## Recipes
You can provide the script a recipe file with the `--recipe` argument. Below are the following supported commands
- lb (Last Block)
- ct (Compression Type)
- tb (Total Bytes)
- lt (Literal)
- tk (Token)
- lc (Literal/Length Codes)
- dc (Distance Codes)
- cl (Code Length Codes)
- cs (Code Symbol)
- hv (Huffman Value)
- rv (Repeat Value)
- zv (Zero Value)
- eb (Extra Bits)
- db (Distance Bits)
- ts (TimeStamp), for Gzip
- os (Operating System), for Gzip
- fl (File Length)
- ck (Checksum)
- dm (Pixel Dimention), for png

For a command, enter the 2 character nmemonic, a colon, the value, and optionally another colon with anything after it (a comment). A token command may look like this:  
`tk: 3,4: 3 characters, go back a distance of 4 to find them`

The recipe file does not need to contain ALL of the commands for an entire session. In theory, your recipe could only contain the commands for the building of just a huffman table. It will only start interpretting those commands when appropriate. The commands obviously still need to be in the order entered as if they were done manually (for the huffman table). For this example, irriflate will interactively ask you for the first/last block, compression type (dynamic in this case), and then the recipe can pick up and enter all the huffman table commands, and then when done, you can go back to interactively entering the tokens.

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
