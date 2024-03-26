import fitz
import os

filedir = os.path.dirname(__file__)

text = """
<style>
body {
    font-family: sans-serif;
    width: 100%;
}

td,
th {
    border: 1px solid blue;
    border-right: none;
    border-bottom: none;
    padding: 5px;
    text-align: center;
}

table {
    width: 100%;
    border-right: 1px solid blue;
    border-bottom: 1px solid blue;
    border-spacing: 0;
}
</style>

<body>
<p><b>Some Colors</b></p>
<table>
    <tr>
    <th>Lime</th>
    <th>Lemon</th>
    <th>Image</th>
    <th>Mauve</th>
    </tr>
    <tr>
    <td>Green</td>
    <td>Yellow</td>
    <td><img src="img-cake.png" width=50></td>
    <td>Between<br>Gray and Purple</td>
    </tr>
</table>
</body>
"""

doc = fitz.Document()

page = doc.new_page()
rect = page.rect + (36, 36, -36, -36)

# we must specify an Archive because of the image
page.insert_htmlbox(rect, text, archive=fitz.Archive("."))

doc.ez_save(__file__.replace(".py", ".pdf"))