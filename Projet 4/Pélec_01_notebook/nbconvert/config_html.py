c = get_config()

c.NbConvertApp.notebooks = ['Pélec_01_notebookexploration.ipynb', 'Pélec_02_notebookmodel.ipynb']
c.NbConvertApp.export_format = 'html'

c.TemplateExporter.exclude_input_prompt = True
c.TemplateExporter.exclude_output_prompt = True