import random
from pyecharts import HeatMap


def valuation():
    """
    两两现券之前的利差的水平分析
    
    :return: 
    """
    pass


from pyecharts import HeatMap, Grid
import random

x_axis = ["1Y", "3Y", "5Y", "7Y", "10Y", "15Y"]
y_axis = ["1Y", "3Y", "5Y", "7Y", "10Y", "15Y"]
data = [[i, j, random.randint(0, 100) / 10.0] for i in range(6) for j in range(6)]
heatmap = HeatMap("国债期限估值差热力图", height=700)
heatmap.add("国债期限估值差", x_axis, y_axis, data, is_visualmap=True,
            visual_top="85%", visual_text_color="grey",
            visual_orient='horizontal', visual_range=[0, 10], visual_pos="center",
            is_label_show=True
            )

grid = Grid()
grid.add(heatmap, grid_bottom="20%")
grid.render()
grid
