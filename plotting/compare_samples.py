"""
compare_samples.py

Compare the same set of variables across four different ROOT Ntuple samples
using matplotlib. The figure layout (rows/columns) automatically adapts to
the number of variables requested.

Requirements:
    pip install uproot awkward numpy matplotlib
    pip install mplhep          # optional, only needed for --hep-style

Example usage:
    python compare_samples.py \
        --files signal.root:tree bkg1.root:tree bkg2.root:tree data.root:tree \
        --labels "Signal" "Background 1" "Background 2" "Data" \
        --variables pt eta phi mass \
        --bins 50 \
        --output comparison.png

    # Per-variable x-axis range, bin count, and display label (repeatable flags):
    python compare_samples.py \
        --files signal.root bkg1.root bkg2.root data.root \
        --labels "Signal" "Background 1" "Background 2" "Data" \
        --variables pt eta mass \
        --range pt 0 150 --range mass 60 120 \
        --var-bins pt 30 --var-bins mass 40 \
        --var-label pt "p_{T} [GeV]" --var-label mass "m_{ll} [GeV]" \
        --output comparison.png

    # Stacked data/MC comparison with naming-based styling (DATA=points,
    # PMU/background=red hatch-or-solid, HAD=green hatch-or-solid, other=blue):
    python compare_samples.py \
        --files data.root pmu_bkg.root had_bkg.root signal.root \
        --labels "DATA" "PMU_background" "HAD_background" "Signal" \
        --variables pt eta phi mass \
        --stack \
        --output comparison.png
    python compare_samples.py \
        --files signal.root bkg1.root bkg2.root data.root \
        --labels "Signal" "Background 1" "Background 2" "Data" \
        --variables pt eta phi mass \
        --hep-style cms --hep-label "Preliminary" \
        --hep-rlabel "138 fb$^{-1}$ (13 TeV)" \
        --output comparison.png

    # Same cut applied to all four samples:
    python compare_samples.py \
        --files signal.root bkg1.root bkg2.root data.root \
        --labels "Signal" "Background 1" "Background 2" "Data" \
        --variables pt eta phi mass \
        --cut "(pt > 30) & (abs(eta) < 2.4) & (njets >= 2)" \
        --output comparison.png

    # A different cut per sample (e.g. blinding the data sample):
    python compare_samples.py \
        --files signal.root bkg1.root bkg2.root data.root \
        --labels "Signal" "Background 1" "Background 2" "Data" \
        --variables pt eta phi mass \
        --cuts "pt > 30" "pt > 30" "pt > 30" "(pt > 30) & ((mass < 100) | (mass > 150))" \
        --output comparison.png

Notes on --files:
    Each entry is "path/to/file.root:tree_name". If you omit ":tree_name",
    the script will try to auto-detect the tree if the file contains only one.

Notes on cuts (--cut / --cuts):
    Cut expressions are plain Python/NumPy boolean expressions evaluated
    against the tree's branches (any branch name used in the tree can be
    referenced, not just the ones being plotted). Use NumPy-style boolean
    operators, NOT Python's "and"/"or"/"not":
        &   instead of  and
        |   instead of  or
        ~   instead of  not
    and wrap each sub-condition in parentheses, e.g.:
        "(pt > 30) & (abs(eta) < 2.4)"
    Cuts are evaluated per-event; branches used only inside the cut (and not
    otherwise plotted) are fetched automatically.

Notes on per-variable plot settings:
    Edit the VARIABLE_CONFIG dict near the top of this file to hardcode your
    standard range/bins/label per variable (recommended for variables you
    plot often). The --range/--var-bins/--var-label CLI flags override
    VARIABLE_CONFIG on a per-run basis without editing the script.

Notes on sample styling:
    Each sample's color/marker/fill is chosen automatically from its --labels
    entry (case-insensitive substring match), mirroring a common ROOT/HEP
    data-vs-MC scheme:
        "DATA"                -> black points with error bars
        "PMU" or "background" -> red, hatched (overlaid) or solid (--stack)
        "HAD"                 -> green, hatched (overlaid) or solid (--stack)
        anything else         -> light blue, semi-transparent solid fill
    Edit get_sample_style() in this file to add/change categories or colors.

RENDERING IS NOT VERY GOOD FOR N VARIABLES > 4
"""

import argparse
import math
import re
import sys
import os

import numpy as np
import matplotlib.pyplot as plt

try:
    import uproot
except ImportError:
    sys.exit(
        "ERROR: the 'uproot' package is required to read ROOT files.\n"
        "Install it with:  pip install uproot awkward"
    )

try:
    import awkward as ak
except ImportError:
    sys.exit(
        "ERROR: the 'awkward' package is required (used internally by uproot "
        "and for applying cuts).\nInstall it with:  pip install awkward"
    )

try:
    import mplhep as hep
    HAS_MPLHEP = True
except ImportError:
    HAS_MPLHEP = False

if "SNDSW_ROOT" in os.environ: prepath = '/eos/home-d/dannc/'
else: prepath = '/Users/danielecentanni/cernbox2/'

def produce_cellist(good_cells=None, cell_cutX=None, cell_cutY=None):
    goodcell_set = None
    cutcell_set = None
    # Load good cells
    if good_cells:
        print(f"Loading good cell list for brick {good_cells}...")
        with open(good_cells) as f:
            goodcell_set = {
                int(line.strip())
                for line in f
                if line.strip().isdigit()
            }
    # Build cells from cuts
    if cell_cutX and cell_cutY and len(cell_cutX) == 2 and len(cell_cutY) == 2:
        print(
            f"Applying cell cuts: X in [{cell_cutX[0]}, {cell_cutX[1]}], "
            f"Y in [{cell_cutY[0]}, {cell_cutY[1]}]"
        )
        cutcell_set = {
            (ycell - 1) * 18 + (xcell - 1)
            for ycell in range(cell_cutY[0], cell_cutY[1] + 1)
            for xcell in range(cell_cutX[0], cell_cutX[1] + 1)
        }
    # Determine output
    if goodcell_set is not None and cutcell_set is not None:
        output_cells = sorted(goodcell_set & cutcell_set)  # intersection
    elif goodcell_set is not None:
        output_cells = sorted(goodcell_set)
    elif cutcell_set is not None:
        output_cells = sorted(cutcell_set)
    else:
        print("No good cell list or cell cuts provided, selecting all cells.")
        output_cells = list(range(324))
    print(f"Final list of selected cells: {output_cells}")
    return output_cells

def getAnalysisTree(filepath, sample, cell_list = None, tree_name = 'vtx_data'):
    from glob import glob
    goodcell_list = []
    cells_added = []
    ncells = 0
    if not cell_list:
        if 'DATA' not in sample:
          cells_added = glob(f'{filepath}/{sample}histos_out_vtxrefit_cell_*_flag1.root')
        else:
          cells_added = glob(f'{filepath}/{sample}_histos_out_vtxrefit_cell_*_flag1.root')
    elif cell_list:
        goodcell_list = cell_list
        #print(f"Loaded {len(goodcell_list)} good cells: {goodcell_list}")
        if 'DATA' not in sample:
            for cell in goodcell_list:
                if not os.path.exists(f'{filepath}/{sample}histos_out_vtxrefit_cell_{cell}_flag1.root'):
                    print(f"### WARNING ###: file {filepath}/{sample}histos_out_vtxrefit_cell_{cell}_flag1.root does not exist, skipping this cell.")
                    continue
                cells_added.append(f'{filepath}/{sample}histos_out_vtxrefit_cell_{cell}_flag1.root')
        else:
            for cell in goodcell_list:
                if not os.path.exists(f'{filepath}/{sample}_histos_out_vtxrefit_cell_{cell}_flag1.root'):
                    print(f"### WARNING ###: file {filepath}/{sample}_histos_out_vtxrefit_cell_{cell}_flag1.root does not exist, skipping this cell.")
                    continue
                cells_added.append(f'{filepath}/{sample}_histos_out_vtxrefit_cell_{cell}_flag1.root')
        #print(f"Added {len(cells_added)} cells to the tree: {cells_added}")
    return cells_added

# --------------------------------------------------------------------------- #
# Hardcoded per-variable plotting configuration
# --------------------------------------------------------------------------- #
# This is the recommended place to pin down your "standard" plotting settings
# for commonly-used variables, so you don't have to repeat --range/--var-bins/
# --var-label on every command line. Anything NOT listed here falls back to
# an auto-detected range, the global --bins value, and the branch name itself
# as the axis label. Per-variable CLI options (--range/--var-bins/--var-label)
# always take priority over these hardcoded defaults.
#
# Format: variable_name -> {"range": (lo, hi), "bins": n_bins, "label": r"..."}
# All three keys are optional; omit any you want auto-determined.
"""VARIABLE_CONFIG = {
    "pt":     {"range": (0, 200),      "bins": 50, "label": r"$p_T$ [GeV]"},
    "eta":    {"range": (-2.5, 2.5),   "bins": 50, "label": r"$\eta$"},
    "phi":    {"range": (-3.15, 3.15), "bins": 50, "label": r"$\phi$ [rad]"},
    "mass":   {"range": (0, 300),      "bins": 60, "label": r"$m$ [GeV]"},
    "njets":  {"range": (0, 10),       "bins": 10, "label": r"$N_{\mathrm{jets}}$"},
}"""

VARIABLE_CONFIG = {
    "ntrks":     {"range": (-0.5, 20.5),      "bins": 21, "label": r"Multiplicity"},
    #"meanIP":    {"range": (0, 3),   "bins": 10, "label": r"Mean Impact Parameter [$\mu$m]"},
    "meanIP":    {"range": (0, 10),   "bins": 50, "label": r"Mean Impact Parameter [$\mu$m]"},
    "prob":    {"range": (0, 1.1), "bins": 20, "label": r"Probability"},
    "np.sqrt(in_tx**2+in_ty**2)":    {"range": (0, 0.1), "bins": 50, "label": r"$\theta_{in}$ [rad]"},
    "np.sqrt(long_tx**2+long_ty**2)":    {"range": (0, 0.1), "bins": 50, "label": r"$\theta_{out}$ [rad]"},
    "kink_angle":    {"range": (0, 0.07), "bins": 15, "label": r"Kink angle [rad]", "log_y": True},
    #"kink_angle":    {"range": (0, 0.1), "bins": 50, "label": r"Kink angle [rad]"},
    "maxaperture":    {"range": (0, 1), "bins": 50, "label": r"Max aperture [rad]"},
}
MERGED_FILE_GROUPS = {
    "MERGED_DATA": [file+':vtx_data' for file in getAnalysisTree(f'{prepath}MuDISemu_analysis/2026/DATA/121/no_sync/', f'DATA_121', produce_cellist(cell_cutX=[3, 15], cell_cutY=[3, 15], good_cells=None))],
}
DERIVED_VARIABLES = {
    "np.sqrt(in_tx**2+in_ty**2)": "np.sqrt(in_tx**2+in_ty**2)",
}


def build_variable_config(variables, default_bins,
                           range_overrides=None, bins_overrides=None,
                           label_overrides=None):
    """
    Merge the hardcoded VARIABLE_CONFIG defaults with any per-variable
    CLI overrides, producing a dict {var: {"range": .., "bins": .., "label": ..}}
    for every requested variable.

    Priority (highest to lowest): CLI override > hardcoded VARIABLE_CONFIG
    > auto/global default.
    """
    range_overrides = range_overrides or {}
    bins_overrides = bins_overrides or {}
    label_overrides = label_overrides or {}

    config = {}
    for var in variables:
        cfg = dict(VARIABLE_CONFIG.get(var, {}))  # copy hardcoded defaults
        cfg.setdefault("range", None)   # None => auto-detect from the data
        cfg.setdefault("bins", default_bins)
        cfg.setdefault("label", var)
        cfg.setdefault("log_y", None)

        if var in range_overrides:
            cfg["range"] = range_overrides[var]
        if var in bins_overrides:
            cfg["bins"] = bins_overrides[var]
        if var in label_overrides:
            cfg["label"] = label_overrides[var]

        config[var] = cfg
    return config

def resolve_variable_expr(var):
    """Return the expression string to evaluate for a given --variables entry."""
    return DERIVED_VARIABLES.get(var, var)  # falls back to the name itself

# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #

def parse_file_spec(spec):
    """
    Split a 'file.root:tree' spec into (file_path, tree_name).
    If no tree name is given, tree_name is None and will be auto-detected.
    """
    if ":" in spec:
        # Guard against Windows-style paths like C:\... by only splitting
        # on the LAST colon, which is what uproot's own convention uses.
        file_path, tree_name = spec.rsplit(":", 1)
    else:
        file_path, tree_name = spec, None
    return file_path, tree_name


def get_tree(file_path, tree_name):
    """Open a ROOT file and return the requested (or auto-detected) TTree."""
    f = uproot.open(file_path)

    if tree_name:
        try:
            return f[tree_name]
        except KeyError:
            sys.exit(f"ERROR: tree '{tree_name}' not found in {file_path}")

    # Auto-detect: look for TTree-like objects at the top level.
    candidates = [
        k.split(";")[0] for k, cls in f.classnames().items()
        if "TTree" in cls
    ]
    candidates = list(dict.fromkeys(candidates))  # de-duplicate, keep order

    if len(candidates) == 1:
        return f[candidates[0]]
    elif len(candidates) == 0:
        sys.exit(f"ERROR: no TTree found in {file_path}")
    else:
        sys.exit(
            f"ERROR: multiple trees found in {file_path}: {candidates}\n"
            f"Specify one explicitly, e.g. '{file_path}:{candidates[0]}'"
        )


def branch_names_in_expression(expr, available):
    """
    Extract identifier tokens from a cut expression and keep only the ones
    that correspond to actual branch names in the tree. This lets a cut
    reference branches that aren't among the plotted --variables without
    the user having to list them twice.
    """
    tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr))
    return tokens & available


def load_sample(file_path, tree_name, variables, cut=None):
    """
    Load the requested branches from a ROOT tree into a dict of numpy arrays,
    optionally applying a boolean selection ('cut') expressed as a Python/
    NumPy expression over branch names (e.g. "(pt > 30) & (abs(eta) < 2.4)").

    Missing plotted branches are reported and skipped (filled with None).
    A cut that references a missing branch is a hard error, since it cannot
    be evaluated.
    """
    if file_path in MERGED_FILE_GROUPS:
        per_file = [
            load_sample(*parse_file_spec(spec), variables, cut=cut)
            for spec in MERGED_FILE_GROUPS[file_path]
        ]
        return {
            var: (np.concatenate([d[var] for d in per_file if d.get(var) is not None])
                  if any(d.get(var) is not None for d in per_file) else None)
            for var in variables
        }
    tree = get_tree(file_path, tree_name)
    available = set(tree.keys())

    # Which plotted variables actually exist in this tree?
    valid_vars = [v for v in variables if v in available]
    for v in variables:
        if v not in available:
            print(f"  [warning] branch '{v}' not found in {file_path} - skipped")

    # Figure out which extra branches the cut expression needs.
    cut_branches = set()
    if cut:
        cut_branches = branch_names_in_expression(cut, available)
        missing_in_cut = branch_names_in_expression(cut, set()) - cut_branches
        # (missing_in_cut is always empty by construction above; real check
        #  happens naturally when eval() below raises NameError instead.)

    expr_map = {var: resolve_variable_expr(var) for var in variables}
    all_expr_branches = set()
    for expr in expr_map.values():
      all_expr_branches |= branch_names_in_expression(expr, available)

    branches_to_read = list(dict.fromkeys(list(all_expr_branches) + list(cut_branches)))
    #branches_to_read = list(dict.fromkeys(valid_vars + list(cut_branches)))
    if not branches_to_read:
        return {v: None for v in variables}

    # Read as awkward arrays so jagged (vector) branches and the cut mask
    # can be handled consistently before flattening for plotting.
    arrays = tree.arrays(branches_to_read, library="ak")

    if cut:
        namespace = {name: arrays[name] for name in cut_branches}
        # Provide a couple of common NumPy-style helper functions for use
        # inside cut expressions (e.g. abs(eta), np.sqrt(...)).
        namespace["abs"] = abs
        namespace["np"] = np
        try:
            mask = eval(cut, {"__builtins__": {}}, namespace)
        except NameError as e:
            sys.exit(f"ERROR: cut expression references an unknown branch: {e}")
        except Exception as e:
            sys.exit(f"ERROR: could not evaluate cut expression '{cut}': {e}")
        arrays = arrays[mask]

    data = {}
    """for var in variables:
        if var not in branches_to_read:
            data[var] = None
            continue
        arr = arrays[var]
        # Flatten jagged (per-object) branches so every jet/lepton/etc. in
        # every event becomes one histogram entry.
        if arr.ndim > 1:
            arr = ak.flatten(arr, axis=None)
        data[var] = np.asarray(ak.to_numpy(arr), dtype=float)"""
    for var in variables:
      expr = expr_map[var]
      if expr in available:            # plain branch, no eval needed
        arr = arrays[expr]
      else:
        ns = {b: arrays[b] for b in branch_names_in_expression(expr, available)}
        ns.update(np=np, abs=abs)
        arr = eval(expr, {"__builtins__": {}}, ns)
      if arr.ndim > 1:
        arr = ak.flatten(arr, axis=None)
      data[var] = np.asarray(ak.to_numpy(arr), dtype=float)
    return data


# --------------------------------------------------------------------------- #
# Plotting
# --------------------------------------------------------------------------- #

def grid_shape(n):
    """Choose a roughly-square (rows, cols) grid for n subplots."""
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    return rows, cols


# Approximate matplotlib equivalents of the ROOT colors used in the original
# PyROOT styling snippet this was ported from.
_ROOT_KGREEN_PLUS2 = "#009900"
_ROOT_RED = "#ff0000"
_ROOT_BLUE_FILL = "#7d99d1"
_ROOT_BLUE_LINE = "#0000ee"


def get_sample_style(label, stack=False):
    """
    Determine drawing style for a sample based on naming conventions,
    mirroring a common ROOT/HEP data-vs-MC plotting scheme (ported from a
    PyROOT snippet keyed on h.GetName()). Matching is case-insensitive and
    based on substrings of `label`:

        - contains "DATA"                  -> black points with error bars
        - contains "PMU" or "BACKGROUND"   -> red; hatched outline when
                                               overlaid, solid fill when
                                               stacked (stack=True)
        - contains "HAD"                   -> green; same hatched/solid rule
        - anything else                    -> light blue, semi-transparent
                                               solid fill (signal-like default)

    To add or change categories, edit this function directly - e.g. add
    another elif branch for a new sample-name keyword.
    """
    name = label.upper()

    if "DATA" in name:
        return {
            "kind": "data",
            "color": "black",
            "marker": "o",
            "markersize": 4,
        }
    elif "EM" in name:
        return {
            "kind": "hist",
            "color": _ROOT_RED,
            "edgecolor": _ROOT_RED,
            "linewidth": 1,
            "hatch": None if stack else "////",
            "alpha": 1.0,
        }
    elif "HAD" in name:
        return {
            "kind": "hist",
            "color": _ROOT_KGREEN_PLUS2,
            "edgecolor": _ROOT_KGREEN_PLUS2,
            "linewidth": 1,
            "hatch": None if stack else "////",
            "alpha": 1.0,
        }
    else:
        return {
            "kind": "hist",
            "color": _ROOT_BLUE_FILL,
            "edgecolor": _ROOT_BLUE_LINE,
            "linewidth": 1,
            "hatch": None,
            "alpha": 0.5,
        }


def plot_comparison(samples_data, labels, variables, var_config, density=True,
                     log_y=False, output=None, title=None, stack=False,
                     hep_style=None, hep_label="Preliminary", hep_rlabel=None,
                     hep_loc=0, weights=None):
    """
    samples_data: list of dicts, one per sample, each {variable: np.array or None}
    labels:       list of sample names (same length as samples_data). Styling
                  per sample is derived from these names - see get_sample_style().
    variables:    list of variable names to plot (one subplot per variable)
    var_config:   dict {variable: {"range": (lo, hi) or None,
                                    "bins": int,
                                    "label": str}}
                  as produced by build_variable_config()
    stack:        if True, non-data ("MC") samples are stacked (cumulative
                  filled bars, solid fill) with data drawn as points on top -
                  the typical data/MC comparison plot. If False (default),
                  samples are overlaid unstacked, with background categories
                  drawn as hatched outlines instead of solid fill so
                  overlapping shapes stay distinguishable.
    hep_style:    one of "cms", "atlas", "lhcb", "alice", or None/"none" to
                  disable mplhep styling entirely.
    hep_label:    status text placed next to the experiment label,
                  e.g. "Preliminary", "Work in Progress", "Internal".
    hep_rlabel:   right-aligned label, typically luminosity/energy, e.g.
                  r"138 fb$^{-1}$ (13 TeV)". If None, mplhep's default is used.
    hep_loc:      mplhep label placement code (see mplhep docs), default 0.
    """
    if stack and density:
        print(
            "[warning] --stack with density normalization mixes normalized "
            "shapes into a stack, which usually isn't physically meaningful. "
            "Forcing density=False for this plot."
        )
        density = False

    use_hep = bool(hep_style) and hep_style.lower() != "none"
    if use_hep:
        if not HAS_MPLHEP:
            print(
                "[warning] mplhep is not installed; run 'pip install mplhep' "
                "for experiment-style plots. Continuing without it."
            )
            use_hep = False
        else:
            style_map = {
                "cms": hep.style.CMS,
                "atlas": hep.style.ATLAS,
                "lhcb": hep.style.LHCb2,
                "alice": hep.style.ALICE,
                "sndlhc": hep.style.SNDLHC,
            }
            style = style_map.get(hep_style.lower())
            if style is None:
                print(f"[warning] unknown --hep-style '{hep_style}'; ignoring.")
                use_hep = False
            else:
                plt.style.use(style)
    if weights is None:
        weights = [1.0] * len(samples_data)
    n_vars = len(variables)
    if n_vars == 3:
      rows, cols = 1, 3
    else:
      rows, cols = grid_shape(n_vars)
    #rows, cols = grid_shape(n_vars)
    active_axes = []
    hep_fontsize = min(13, 18 - 1.5 * max(rows, cols))
    #hep_fontsize = 12

    # Scale the figure size with the grid so panels stay readable
    per_panel_w = 7.0 if cols==1 else 5.5
    fig_w = per_panel_w * cols
    extra_row_height = 0.6 if use_hep else 0.0   
    fig_h = (5.1 + extra_row_height) * rows        
    fig, axes = plt.subplots(rows, cols, figsize=(fig_w, fig_h), squeeze=False)
    axes_flat = axes.flatten()

    for i, var in enumerate(variables):
        ax = axes_flat[i]
        cfg = var_config.get(var, {"range": None, "bins": 50, "label": var, "log_y": None})
        var_log_y = cfg.get("log_y")
        if var_log_y is None:
            var_log_y = log_y

        # Determine the binning range: explicit config wins, otherwise
        # auto-detect the common range across all samples that have data.
        all_vals = [
            sdata[var] for sdata in samples_data
            if sdata.get(var) is not None and len(sdata[var]) > 0
        ]
        if not all_vals:
            #ax.set_title(f"{var} (no data)")
            #ax.axis("off")
            continue

        if cfg.get("range") is not None:
            lo, hi = cfg["range"]
        else:
            lo = min(v.min() for v in all_vals)
            hi = max(v.max() for v in all_vals)
            if lo == hi:
                lo, hi = lo - 0.5, hi + 0.5

        n_bins = cfg.get("bins", 50)
        bin_edges = np.linspace(lo, hi, n_bins + 1)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        bin_widths = np.diff(bin_edges)
        active_axes.append(ax)

        stack_bottom = np.zeros(n_bins)
        max_y = 0
        data_entry = None  # drawn last, so points sit on top of any fills

        """ordered = sorted(
        zip(samples_data, labels),
        key=lambda pair: 1 if (stack and "DIS" in pair[1].upper()) else 0,
        )
        for sdata, label in ordered:
            vals = sdata.get(var)
            if vals is None or len(vals) == 0:
                continue

            style = get_sample_style(label, stack=stack)

            if style["kind"] == "data":
                # Defer data so it's always drawn on top, after MC fills.
                data_entry = (vals, style, label)
                continue

            # Values outside a manually-set range fall into the edge bins
            # via np.histogram's `bins=` edges, so they're still counted at
            # the boundaries rather than silently dropped.
            counts, _ = np.histogram(vals, bins=bin_edges, density=density)"""
        samples = list(zip(samples_data, labels, weights))
        if stack:
            samples = sorted(samples, key=lambda t:1 if "DIS" in t[1].upper() else 0)
        for sdata, label, w in samples:
            vals = sdata.get(var)
            if vals is None or len(vals) == 0:
                continue
            style = get_sample_style(label, stack=stack)
            if style["kind"] == "data":
                data_entry = (vals, style, label)
                continue
            
            counts, _ = np.histogram(vals, bins=bin_edges, density=density)
            if not density:
                counts = counts * w

            if stack:
                ax.bar(
                    bin_centers, counts, width=bin_widths, bottom=stack_bottom,
                    color=style["color"], edgecolor=style["edgecolor"],
                    linewidth=0, alpha=style["alpha"],
                    label=label,
                )
                stack_bottom = stack_bottom + counts
                max_y = max(max_y, stack_bottom.max())
                top_edge = np.append(stack_bottom, stack_bottom[-1])
                ax.step(bin_edges, top_edge, where='post',
                        color=style['edgecolor'], linewidth=style["linewidth"])
            elif style["hatch"]:
                # Hatched outline only (no solid fill), similar to ROOT's
                # FillStyle(3004) diagonal-hatch pattern used when overlaid.
                ax.hist(
                    vals, bins=bin_edges, density=density,
                    histtype="stepfilled", facecolor="none",
                    edgecolor=style["edgecolor"], hatch=style["hatch"],
                    linewidth=style["linewidth"], label=label,
                )
            else:
                ax.hist(
                    vals, bins=bin_edges, density=density,
                    histtype="stepfilled",
                    facecolor=style["color"], edgecolor=style["edgecolor"],
                    alpha=style["alpha"], linewidth=style["linewidth"],
                    label=label,
                )
            """elif style["hatch"]:
                # Hatched outline only (no solid fill), similar to ROOT's
                # FillStyle(3004) diagonal-hatch pattern used when overlaid.
                ax.stairs(
                    counts, bin_edges, fill=True,
                    facecolor="none",edgecolor=style["edgecolor"], hatch=style["hatch"],
                    linewidth=style["linewidth"], label=label,
                )
            else:
                ax.stairs(
                    counts, bin_edges,
                    fill=True,
                    facecolor=style["color"], edgecolor=style["edgecolor"],
                    alpha=style["alpha"], linewidth=style["linewidth"],
                    label=label,
                )"""
            if not stack:
                max_y = max(max_y, counts.max())

        if data_entry is not None:
            vals, style, label = data_entry
            raw_counts, _ = np.histogram(vals, bins=bin_edges, density=False)
            counts, _ = np.histogram(vals, bins=bin_edges, density=density)
            errors = np.sqrt(raw_counts)
            if density:
                # Rescale Poisson errors by the same per-bin normalization
                # factor np.histogram applied to get `counts` from raw counts.
                scale = np.divide(
                    counts, raw_counts,
                    out=np.zeros_like(counts, dtype=float),
                    where=raw_counts > 0,
                )
                errors = errors * scale
            max_y = max(max_y, (counts+errors).max())
            ax.errorbar(
                bin_centers, counts, yerr=errors,
                fmt=style["marker"], color=style["color"],
                markersize=style["markersize"], linestyle="none",
                elinewidth=1, capsize=2, capthick=1,
                label=label, zorder=10,
            )

        if var_log_y:
            ax.set_yscale("log")
            if max_y > 0:
                ax.set_ylim(top=max_y * 100)
        else:
            if max_y > 0:
                ax.set_ylim(top=max_y * 1.35)

        ax.set_xlim(lo, hi)
        ax.set_xlabel(cfg.get("label", var))
        ax.set_ylabel("Normalized entries" if density else "Entries")
        ax.legend(fontsize=12)
        ax.grid(alpha=0.3)

        """if use_hep:
            label_fn = {
                "cms": getattr(hep, "cms", None),
                "atlas": getattr(hep, "atlas", None),
                "lhcb": getattr(hep, "lhcb", None),
                "alice": getattr(hep, "alice", None),
                "sndlhc": getattr(hep, "sndlhc", None),
            }.get(hep_style.lower())
            if label_fn is not None:
                try:
                    kwargs = dict(ax=ax, loc=hep_loc, label=hep_label, fontsize=hep_fontsize)
                    if hep_rlabel is not None:
                        kwargs["rlabel"] = hep_rlabel
                    label_fn.label(**kwargs)
                except Exception as e:
                    print(f"[warning] mplhep label failed for '{var}': {e}")"""

    # Hide any unused subplot slots (when n_vars doesn't fill the grid exactly)
    for j in range(n_vars, len(axes_flat)):
        axes_flat[j].axis("off")

    if title:
        fig.suptitle(title, fontsize=14)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
    else:
        fig.tight_layout()
    """if use_hep:
        fig.subplots_adjust(hspace=0.5)"""
    if use_hep:
      fig.subplots_adjust(hspace=0.3, top=0.92)
      fig.canvas.draw()
      label_fn = {
          "cms": getattr(hep, "cms", None),
          "atlas": getattr(hep, "atlas", None),
          "lhcb": getattr(hep, "lhcb", None),
          "alice": getattr(hep, "alice", None),
          "sndlhc": getattr(hep, "sndlhc", None),
      }.get(hep_style.lower())
      if label_fn is not None:
        for ax in active_axes:  
          try:
            kwargs = dict(ax=ax, loc=hep_loc, llabel=hep_label, fontsize=hep_fontsize)
            if hep_rlabel is not None:
              kwargs["rlabel"] = hep_rlabel
              label_fn.label(**kwargs)
          except Exception as e:
            print(f"[warning] mplhep label failed: {e}")
    if output:
        fig.savefig(output, dpi=150)
        print(f"Saved figure to: {output}")
    else:
        plt.show()

    return fig


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(
        description="Compare Ntuple variables across four ROOT samples with matplotlib."
    )
    parser.add_argument(
        "--files", nargs=4, required=True, metavar="FILE[:TREE]",
        help="Exactly 4 ROOT files, each optionally as path.root:treename",
    )
    parser.add_argument(
        "--labels", nargs=4, required=True,
        help="Legend labels for the 4 samples, e.g. Signal Bkg1 Bkg2 Data",
    )
    parser.add_argument(
        "--variables", nargs="+", required=True,
        help="One or more branch/variable names to plot",
    )
    cut_group = parser.add_mutually_exclusive_group()
    cut_group.add_argument(
        "--cut", default=None,
        help=(
            "Single selection cut applied to ALL four samples, as a NumPy-style "
            "boolean expression using branch names, e.g. "
            "\"(pt > 30) & (abs(eta) < 2.4)\". Use & | ~ instead of and/or/not."
        ),
    )
    cut_group.add_argument(
        "--cuts", nargs=4, default=None, metavar="CUT",
        help=(
            "Four selection cuts, one per sample (same order as --files/--labels), "
            "for when samples need different selections (e.g. a blinding cut on data)."
        ),
    )
    parser.add_argument("--bins", type=int, default=50,
                         help="Default number of histogram bins (used unless overridden "
                              "per-variable via --var-bins or VARIABLE_CONFIG)")

    var_group = parser.add_argument_group(
        "per-variable overrides",
        "Override range/bins/label for individual variables. Repeatable. "
        "These take priority over the hardcoded VARIABLE_CONFIG dict in the script.",
    )
    var_group.add_argument(
        "--range", nargs=3, action="append", metavar=("VAR", "MIN", "MAX"),
        help="Set the x-axis range for one variable, e.g. --range pt 0 200",
    )
    var_group.add_argument(
        "--var-bins", nargs=2, action="append", metavar=("VAR", "NBINS"),
        help="Set the number of bins for one variable, e.g. --var-bins pt 40",
    )
    var_group.add_argument(
        "--var-label", nargs=2, action="append", metavar=("VAR", "LABEL"),
        help='Set the displayed x-axis label for one variable, e.g. '
             '--var-label pt "p_{T} [GeV]"',
    )

    hep_group = parser.add_argument_group("mplhep / experiment styling")
    hep_group.add_argument(
        "--hep-style", choices=["cms", "atlas", "lhcb", "alice", "sndlhc", "none"], default="sndlhc",
        help="Apply an experiment plot style via mplhep (requires 'pip install mplhep')",
    )
    hep_group.add_argument(
        "--hep-label", default="Preliminary",
        help='Status text next to the experiment label, e.g. "Preliminary", '
             '"Work in Progress", "Internal" (default: Preliminary)',
    )
    hep_group.add_argument(
        "--hep-rlabel", default=None,
        help='Right-aligned label, typically luminosity/energy, e.g. '
             '"138 fb$^{-1}$ (13 TeV)"',
    )
    hep_group.add_argument(
        "--hep-loc", type=int, default=0,
        help="mplhep label location code (see mplhep docs), default: 0",
    )
    parser.add_argument(
        "--stack", action="store_true",
        help="Stack non-data samples as cumulative solid-filled bars (with data "
             "drawn as points on top), instead of the default overlaid/hatched "
             "comparison. Naming-based styling is applied either way - see "
             "get_sample_style() in the script.",
    )
    parser.add_argument(
        "--no-density", action="store_true",
        help="Plot raw entry counts instead of normalized (density) histograms",
    )
    parser.add_argument("--log-y", action="store_true", help="Use log scale on the y-axis")
    parser.add_argument("--title", default=None, help="Overall figure title")
    parser.add_argument(
        "--output", default=None,
        help="Output image path (e.g. comparison.png). If omitted, shows interactively.",
    )
    parser.add_argument(
    "--weights", nargs=4, type=float, default=[1.]+[len(MERGED_FILE_GROUPS["MERGED_DATA"])/324]*3, metavar="W",
    help="Flat scalar weight per sample (same order as --files/--labels), "
         "applied to MC histogram counts only when NOT using --no-density "
         "is false... (i.e. only in raw-count mode, since normalized "
         "densities would just undo the scaling). Data is never weighted.",
    )
    args = parser.parse_args()

    # Resolve the cut to apply per sample: a shared --cut, four --cuts, or none.
    if args.cuts:
        cuts = args.cuts
    elif args.cut:
        cuts = [args.cut] * 4
    else:
        cuts = [None] * 4

    print("Loading samples...")
    samples_data = []
    for spec, label, cut in zip(args.files, args.labels, cuts):
        file_path, tree_name = parse_file_spec(spec)
        cut_msg = f", cut='{cut}'" if cut else ""
        print(f"  - {label}: {file_path} (tree={tree_name or 'auto'}{cut_msg})")
        samples_data.append(load_sample(file_path, tree_name, args.variables, cut=cut))

    # Resolve per-variable range/bins/label overrides from the CLI, then merge
    # with the hardcoded VARIABLE_CONFIG defaults defined near the top of the file.
    range_overrides = {}
    if args.range:
        for var, lo, hi in args.range:
            range_overrides[var] = (float(lo), float(hi))

    bins_overrides = {}
    if args.var_bins:
        for var, nbins in args.var_bins:
            bins_overrides[var] = int(nbins)

    label_overrides = {}
    if args.var_label:
        for var, lbl in args.var_label:
            label_overrides[var] = lbl

    var_config = build_variable_config(
        args.variables, default_bins=args.bins,
        range_overrides=range_overrides,
        bins_overrides=bins_overrides,
        label_overrides=label_overrides,
    )

    plot_comparison(
        samples_data=samples_data,
        labels=args.labels,
        variables=args.variables,
        var_config=var_config,
        density=not args.no_density,
        log_y=args.log_y,
        output=args.output,
        title=args.title,
        stack=args.stack,
        hep_style=args.hep_style,
        hep_label=args.hep_label,
        hep_rlabel=args.hep_rlabel,
        hep_loc=args.hep_loc,
        weights = args.weights
    )


if __name__ == "__main__":
    main()


"""if __name__ == "__main__":
  main()
  Varlist = ['ntrks', 'meanIP', 'prob']
  xRanges = [[-0.5,20.5], [0, 10], [0, 1.1]]
  nBins = [21, 50, 20]
  sel = '1'"""


# CL for last cut B121 : 
# python ~/cernbox2/software-macros/plotting/compare_samples.py --files MERGED_DATA MC/muon_Euniform_RUN1_FLUKA25/121/DIShistos_out_vtxrefit_flag1_energy.root:vtx_data MC/muon_Euniform_RUN1_FLUKA25/121/PMUhistos_out_vtxrefit_flag1_energy.root:vtx_data MC/muon_Euniform_RUN1_FLUKA25/121/HADhistos_out_vtxrefit_flag1_energy.root:vtx_data --labels "Data" "Signal (DIS)" "Background (EM)" "Background (HAD)" --variables ntrks meanIP --hep-style sndlhc --hep-rlabel '40 kg$\times$5.0 fb$^{-1}$ $\sqrt{s}$=13.6 TeV' --cuts "(((plate != 40) & (plate != 41)) | (vy < 90000)) & ((plate != 4) | (vy < 150000)) & (ntrks > 4) & (meanIP < 2.5) & (maxaperture > 0.1) & (np.sqrt(long_tx**2 + long_ty**2) < 0.02) & (np.sqrt(in_tx**2 + in_ty**2) < 0.02) & (kink_angle < 0.05)" "(ntrks > 4) & (meanIP < 2.5) & (maxaperture > 0.1) & (np.sqrt(long_tx**2 + long_ty**2) < 0.02) & (np.sqrt(in_tx**2 + in_ty**2) < 0.02) & (kink_angle < 0.05)" "(ntrks > 4) & (meanIP < 2.5) & (maxaperture > 0.1) & (np.sqrt(long_tx**2 + long_ty**2) < 0.02) & (np.sqrt(in_tx**2 + in_ty**2) < 0.02) & (kink_angle < 0.05)" "(ntrks > 4) & (meanIP < 2.5) & (maxaperture > 0.1) & (np.sqrt(long_tx**2 + long_ty**2) < 0.02) & (np.sqrt(in_tx**2 + in_ty**2) < 0.02) & (kink_angle < 0.05)" --stack

# python ~/cernbox2/software-macros/plotting/compare_samples.py --files MERGED_DATA MC/muon_Euniform_RUN1_FLUKA25/121/DIShistos_out_vtxrefit_flag1_energy.root:vtx_data MC/muon_Euniform_RUN1_FLUKA25/121/PMUhistos_out_vtxrefit_flag1_energy.root:vtx_data MC/muon_Euniform_RUN1_FLUKA25/121/HADhistos_out_vtxrefit_flag1_energy.root:vtx_data --labels "Data" "Signal (DIS)" "Background (EM)" "Background (HAD)" --variables ntrks meanIP --hep-rlabel '40 kg$\times$5.0 fb$^{-1}$ $\sqrt{s}$=13.6 TeV' --cuts "(((plate != 40) & (plate != 41)) | (vy < 90000)) & ((plate != 4) | (vy < 150000))" "None" "None" "None"