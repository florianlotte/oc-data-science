c = get_config()

c.NbConvertApp.notebooks = [
    'P6_01_notebookexploration.ipynb',
    'P6_02_notebookbagofword.ipynb',
    'P6_03_notebookembedding.ipynb',
    'P6_04_notebookimages.ipynb'
]
c.NbConvertApp.export_format = 'html'

c.TemplateExporter.exclude_input_prompt = True
c.TemplateExporter.exclude_output_prompt = True