from tensile_analyzer import *
import os
import matplotlib.pyplot as plt
import sys

colors = np.array([
    [255, 0, 0],
    [143, 35, 35],
    [0, 234, 255],
    [170, 0, 255],
    [255, 127, 0],
    [191, 255, 0],
    [0, 149, 255],
    [255, 0, 170],
    [255, 212, 0],
    [106, 255, 0],
    [0, 64, 255],
    [237, 185, 185],
    [204, 204, 204],
    [231, 233, 185],
    [220, 185, 237],
    [185, 237, 224],
    [143, 35, 35],
    [35, 98, 143],
    [143, 106, 35],
    [107, 35, 143],
    [79, 143, 35],
    [0, 0, 0],
    [115, 115, 115],
    [255, 215, 0]
]) / 255.0

class ReportGenerator:
    def __init__(self,machine):
        self.data =  {}
        self.machine = machine

    def table_generator(self):
            # generate latex table first
            table = []
            table_header = "\\begin{{longtable}}{{|c|c|c|c|c|}} \\hline \\textbf{{Sample Name}} & \\textbf{{UTS (MPa)}} & \\textbf{{{:}\% YS (MPa)}} & \\textbf{{Break Strain (\%)}} &\\textbf{{Young's Modulus (MPa)}}\\\ \\hline ".format(self.offset*100)
            table.append(table_header)

            idx =  0

            for key in self.data:          
                color_rgb = [1, .980, 0]  # <- HERE IS AN EXAMPLE OF HOW TO DO THE COLOR YOU WANTED.... I THINK.
                # writes each column of data
                #print(str(key).split('.')[0])
                name = key.split('/')[-1]
                name = name.split('.')[0]
                name = name.replace("_","\_")
                table_data = """\\definecolor{{{}}}{{rgb}}{{{}, {}, {}}}\\tikz\\draw[{},fill={}] (0,0) circle (.7ex); {} & {:.2f} & {:.2f} & {:.3f} & {:.3f}\\\ \\hline """.format(idx, *colors[idx], idx, idx, name, self.data[key]['uts'], self.data[key]['ys'], self.data[key]['elongation'], self.data[key]['youngs'][0])
                table.append(table_data)
                idx+=1

            table_close = '\\end{longtable}'
            table.append(table_close)
            # FIXME: absolute path
            d = open('data.tex', 'w')
            d.write(''.join(table))
            d.close()

    def graph_generator(self, draw_ys_lines: bool = False):
        idx = 0
        for key in self.data:          
            params = {"ytick.color": "black",
                    "xtick.color": "black",
                    "axes.labelcolor": "black",
                    "axes.edgecolor": "black",
                    "text.usetex": True,
                    "font.family": "serif",
                    "font.serif": ["Computer Modern Serif"]}
            plt.rcParams.update(params)
            plt.ylabel("Stress (MPa)")
            plt.xlabel("Strain (mm/mm)")


            
            plt.plot(self.data[key]["x"],self.data[key]["y"],label=key,color=colors[idx])
            
            if draw_ys_lines:
                plt.axline((self.data[key]["offset"],self.data[key]["intercept"]),slope=self.data[key]["youngs"][0],color= 'black')
            
            idx+=1


        plt.grid()
        plt.savefig("collatedData.pdf", bbox_inches='tight', format='pdf')
        plt.style.use('default')
    

            
    def load_data(self, path: str,offset: float = .02):
        x, y = get_data(path,self.machine)
        model = calculate_youngs(x,y,.1,.2)
        ys = calculate_ys(x,y,model,offset)
        uts = calculate_uts(x,y)
        elongation = calculate_strain_at_break(x,y)
        self.offset = offset
        self.data.update({path:{'x':x,
                                    'y':y,
                                    'ys':ys,
                                    'youngs':model.coef_,
                                    'intercept':model.intercept_,
                                    'uts':uts,
                                    'elongation':elongation,
                                    'offset': offset,
                                    }})    
        self.data = {key:value for key, value in sorted(self.data.items())}    



class  CumulativeReport(ReportGenerator):
     def __init__(self,directory,machine):
        super().__init__(machine)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".csv"): 
                print(f'found {os.path.join(directory, filename)}')
                super().load_data(os.path.join(directory, filename),offset = .02)
                
            else:
                pass
          
class  SingleReport(ReportGenerator):
     def __init__(self,filename,machine):
        super().__init__(machine)
        super().load_data(filename,offset = .002)
        

if __name__ == '__main__':
    if os.path.isfile(sys.argv[1]):
        taffy_single = SingleReport(filename=sys.argv[1],machine='gom')
        print('running single report')
        taffy_single.table_generator()
        taffy_single.graph_generator(draw_ys_lines=True)
        

    if os.path.isdir(sys.argv[1]):
        taffy = CumulativeReport(directory=sys.argv[1],machine='gom')
        taffy.table_generator()
        taffy.graph_generator()
    
    
    





