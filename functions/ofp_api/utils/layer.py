import pandas as pd
import jenkspy

def prepare_layer_info(
          df, 
          value_name, 
          legend_title,
          n_classes = 5, 
          start_color="#F5A7C1", 
          end_color="#752842",
          breaks=None):
        
        if not breaks:
            breaks = jenkspy.jenks_breaks(df[value_name], n_classes=n_classes)
            breaks = list(set(breaks))
            breaks.sort()
            n_classes = len(breaks)-1
        color_ramp = interpolate_color(start_color, end_color, n_classes)
        legend_bins =  [{ color_ramp[i] : f'{int(breaks[i])} - {int(breaks[i+1])}' } for i in range(n_classes) ] 
     
        df[f'{value_name}_color'] = pd.cut(df[value_name], bins=breaks, include_lowest=True, labels=color_ramp)
        return  {
             "layer_name" : value_name,
             "data": df[[value_name, f'{value_name}_color']],
             "legend": {
                "title": legend_title,
                "bins" : legend_bins           
             }
        }




def interpolate_color(start_color, end_color, n_classes):
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    step = [(e - s) / (n_classes - 1) for s, e in zip(start_rgb, end_rgb)]
    color_ramp = [
        rgb_to_hex((int(start_rgb[0] + step[0]*i),
                    int(start_rgb[1] + step[1]*i),
                    int(start_rgb[2] + step[2]*i)))
        for i in range(n_classes)
    ]
    return color_ramp


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)