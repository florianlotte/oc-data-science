c = get_config()

c.NbConvertApp.notebooks = [
    'P8_01_notebookexploration.ipynb',
]
c.NbConvertApp.export_format = 'html'

c.TemplateExporter.exclude_input_prompt = True
c.TemplateExporter.exclude_output_prompt = True