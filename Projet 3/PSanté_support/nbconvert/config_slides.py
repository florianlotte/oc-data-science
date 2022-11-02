c = get_config()

c.NbConvertApp.notebooks = ['PSanté_01_notebooknettoyage.ipynb', 'PSanté_02_notebookexploration.ipynb']
c.NbConvertApp.export_format = 'slides'

c.SlidesExporter.reveal_theme = 'simple'
c.SlidesExporter.reveal_transition = 'none'
c.SlidesExporter.reveal_scroll = True

c.TemplateExporter.exclude_input_prompt = True
c.TemplateExporter.exclude_output_prompt = True

c.TemplateExporter.template_file = 'nbconvert/template/custom_index.html.j2'