import mff_pytex as ptx
from datetime import date
import pandas as pd
import numpy as np
import os

texfile = ptx.TexFile('myfile')

preamble = texfile.preamble
preamble.author = 'John Smith'
preamble.title = 'My first document'
preamble.date = date.today()
preamble.documentclass = ptx.DocumentClass('article')

body = texfile.document
body.maketitle()
body.write('Some text')

body.write(ptx.command('section', 'Lists'))
arr = ptx.List(['dog', 'cat'])
arr.items(['apple', 'banana'])
body.add(arr)

body.write(ptx.command('section', 'Tables'))
s = pd.Series([1, 3, 5, np.nan, 6, 8])
body.add(ptx.Table(s))

body.write(ptx.command('section', 'Pictures'))
image = ptx.Picture('tex.png', caption='My first picture', settings=['height=1cm'])
image.write(ptx.command('centering'))
body.add(image)

body.write(ptx.command('section', 'Packages'))
package = ptx.Package('lipsum')
ptx.add_package(package)
body.write(ptx.command('lipsum'))

bib = ptx.Bibliography('sample')
bib.add(ptx.Book('rome', 'The History of the Decline and Fall of the Roman Empire', 1776, 'Edward Gibbon', 'Strahan and Cadell, London'))
bib.create()

body.write(ptx.command('section', 'Bibliography'))
body.write('My first citation ' + ptx.command('cite', 'rome'))
body.newpage()
body.bibliography('sample')
preamble.write(ptx.command('bibliographystyle', 'unsrtnat'))

texfile.create()

texfile.make_pdf()
