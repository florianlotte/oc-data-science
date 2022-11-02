c = get_config()

c.NbConvertApp.notebooks = ['P5_01_notebooknettoyage.ipynb', 'P5_02_notebookanalyse.ipynb', 'P5_03_notebookproduction.ipynb']
c.NbConvertApp.export_format = 'html'

c.TemplateExporter.exclude_input_prompt = True
c.TemplateExporter.exclude_output_prompt = True