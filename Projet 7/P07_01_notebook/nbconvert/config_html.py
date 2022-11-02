c = get_config()

c.NbConvertApp.notebooks = [
    'P7_01_notebookexploration.ipynb',
    'P7_02_notebookscoring.ipynb',
    'P7_03_notebookdashboard.ipynb'
]
c.NbConvertApp.export_format = 'html'

c.TemplateExporter.exclude_input_prompt = True
c.TemplateExporter.exclude_output_prompt = True