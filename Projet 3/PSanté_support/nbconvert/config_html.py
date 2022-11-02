c = get_config()

c.NbConvertApp.notebooks = ['PSanté_01_notebooknettoyage.ipynb', 'PSanté_02_notebookexploration.ipynb']
c.NbConvertApp.export_format = 'html'

c.TemplateExporter.exclude_input_prompt = True
c.TemplateExporter.exclude_output_prompt = True