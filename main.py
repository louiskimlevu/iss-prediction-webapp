#!/usr/bin/env python
from flask import Flask, render_template, flash, request, jsonify, Markup
import matplotlib
import matplotlib.pyplot as plt
import io, os, base64
import numpy as np
import pandas as pd

# global variables
# instantiate the Flask server
app = Flask(__name__)
pop_df = None
location_list = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.before_first_request
def startup():
	global pop_df, location_list

	# load and prepare the data
	pop_df = pd.read_csv(BASE_DIR + '/WPP2019_PopulationByAgeSex.csv')
	location_list = sorted(list(set(pop_df['Location'])))

def get_population_pyramid(country, year):
	pop_df_tmp = pop_df[(pop_df['Location']==country) & (pop_df['Time']==year)].copy()
	pop_df_tmp = pop_df_tmp.sort_values('AgeGrpStart',ascending=True)
	return(pop_df_tmp)

@app.route("/", methods=['POST', 'GET'])
def build_pyramid():
	plot_to_show = ''
	selected_country = ''
	# country_list = ''
	selected_year = ''

	if request.method == 'POST':
		selected_country = request.form['selected_country']
		selected_year = int(request.form['selected_year'])

		pop_df_tmp = get_population_pyramid(selected_country, selected_year)

		y = range(0, len(pop_df_tmp))
		x_male = pop_df_tmp['PopMale']
		x_female = pop_df_tmp['PopFemale']

		# max xlim
		max_x_scale = max(max(x_female), max(x_male))

		fig, axes = plt.subplots(ncols=2, sharey=True, figsize=(12, 10))

		fig.patch.set_facecolor('xkcd:Beige')
		plt.figtext(.5,.9,selected_country + ": " +  str(selected_year), fontsize=15, ha='center')

		axes[0].barh(y, x_male, align='center', color='lightblue')
		axes[0].set(title='Males')
		axes[0].set(xlim=[0,max_x_scale])
		axes[1].barh(y, x_female, align='center', color='pink')
		axes[1].set(title='Females')
		axes[1].set(xlim=[0,max_x_scale])
		axes[1].grid()
		axes[0].set(yticks=y, yticklabels=pop_df_tmp['AgeGrp'])
		axes[0].invert_xaxis()
		axes[0].grid()

        # no plot.show() but we save in a memory space pointer
		img = io.BytesIO()
		plt.savefig(img, format='png')
		img.seek(0)
        # encode de the image in a string
		plot_url = base64.b64encode(img.getvalue()).decode()
		plot_to_show = Markup('<img src="data:image/png;base64,{}" style="width:100%;vertical-align:top">'.format(plot_url))

	return render_template('build-a-pyramid.html',
						plot_to_show = plot_to_show,
						selected_country = selected_country,
						location_list = location_list,
						selected_year = selected_year)

if __name__=='__main__':
    app.run(debug=True)