from Lib.class_Vs_profile import Vs_Profile
from Lib.class_ground_motion import Ground_Motion
from Lib.class_hh_calibration import HH_Calibration
from Lib.class_damping_calibration import Damping_Calibration
from Lib.class_simulation import Nonlinear_Simulation
from Lib.class_batch_simulation import Batch_Simulation
from Numpy_txt import read_file
import numpy as np
from pandas import read_excel, DataFrame, ExcelWriter
from Lib.helper_site_response import response_spectra
import os

file_name = "soil_generations.xlsx"
sheet_name = os.environ.get("sheet_name", "Vs150")
folder_name = os.environ.get("folder_name", "low")
excel = read_excel(file_name, sheet_name=sheet_name)
print(sheet_name, folder_name)


def create_profile(vs1, vs2, vs3):
    return np.array(
        [
            [10, vs1, 0.05, 1800, 1],
            [10, vs2, 0.05, 1800, 2],
            [10, vs3, 0.05, 1800, 3],
            [0, 2000, 0.05, 1800, 0],
        ]
    )


folder = os.path.join("files", folder_name)
input_accels = []
files = os.listdir(folder)
all_dfs = {}


def create_sa_dict():
    sa_dict = {}
    for i in range(excel.shape[0]):
        sa_dict[i] = {}
        for f in files:
            sa_dict[i][f] = np.zeros(500)
    return sa_dict


sa_dict = create_sa_dict()

for f in files:
    acc, dt = read_file(os.path.join(folder, f))
    input_accel = Ground_Motion(acc, dt=dt, unit="g")
    input_accels.append(input_accel)
    print(np.max(acc))
    all_dfs[f] = {
        "vs1": [],
        "vs2": [],
        "vs3": [],
        "Fa": [],
        "Fv": [],
        "pga": [],
    }


def run(index):
    row = excel.iloc[index, :]
    vs1 = row.vs1
    vs2 = row.vs2
    vs3 = row.vs3
    vs_profile = Vs_Profile(create_profile(vs1, vs2, vs3))
    hh_c = HH_Calibration(vs_profile)
    hh_g_param = hh_c.fit(verbose=False)
    d_c = Damping_Calibration(vs_profile)
    hh_x_param = d_c.get_HH_x_param(
        parallel=True,  # set `parallel` to `True` to use multiple CPU cores
        pop_size=200,
        n_gen=100,  # pop_size and n_gen control the speed and accuracy of the fit
        show_fig=False,
    )
    batch_sim = Batch_Simulation(
        [
            Nonlinear_Simulation(
                vs_profile,
                acc,
                G_param=hh_g_param,
                xi_param=hh_x_param,
                boundary="rigid",
            )
            for acc in input_accels
        ]
    )

    sim_results = batch_sim.run(
        parallel=True, n_cores=5, options=dict(remove_sim_dir=True, show_fig=False)
    )
    for i, r in enumerate(sim_results):
        acc_inp =input_accels[i].accel
        ri = response_spectra(acc_inp,0.02,10,500)
        _, sa_ri, _, _, _, _, _ = ri
        sa_ri = sa_ri /9.81
        acc = r.accel_on_surface.accel
        rs = response_spectra(acc, 0.02, 10, 500)
        _, sa, _, _, _, _, _ = rs
        sa = sa/9.81
        pga = r.accel_on_surface.pga_in_g
        Fa = sa[9] /sa_ri[9]   # Calculate ss using the provided formula
        Fv = sa[49] /sa_ri[49] 
        all_dfs[files[i]]["Fv"].append(Fv)
        all_dfs[files[i]]["Fa"].append(Fa)
        all_dfs[files[i]]["vs1"].append(vs1)
        all_dfs[files[i]]["vs2"].append(vs2)
        all_dfs[files[i]]["vs3"].append(vs3)
        all_dfs[files[i]]["pga"].append(pga)

        sa_dict[index][files[i]] = sa
        print((np.max(acc)),np.max(acc_inp))


def to_excel():
    with ExcelWriter(f"{sheet_name}_output_{folder_name}.xlsx") as writer:
        for f in files:
            df: DataFrame = DataFrame(all_dfs[f])
            df.to_excel(writer, sheet_name=f, index=False)

    with ExcelWriter(f"{sheet_name}_response_{folder_name}.xlsx") as writer:
        for i in range(excel.shape[0]):
            df: DataFrame = DataFrame(sa_dict[i])
            df.to_excel(writer, sheet_name=f"Row-{i}", index=False)


if __name__ == "__main__":
    import os

    for i in range(len(excel)):
        
        try:
            run(i)
            print(i + 1, len(excel))  
        except Exception as e:
            print(e)

    to_excel()
