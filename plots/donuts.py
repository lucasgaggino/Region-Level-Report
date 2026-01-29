import matplotlib.pyplot as plt
import pandas as pd
from mat_client import MATClient


def plot_fig1_donuts(res_data):
    """Plot donut charts for vCPU, Memoria, and Disco resources."""
    
    resources = ["vCPU", "Memoria", "Disco"]

    # Colores (igual al notebook)
    c_sys = "#7f7f7f"
    c_res = "#e67e22"
    c_spare = "#87CEEB"
    c_free = "#2ecc71"
    c_frag = "#8E44AD"

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for i, res in enumerate(resources):
        df = res_data[res]["df"]
        ax = axes[i]

        vals = [df["v_sys"].sum(), df["v_res"].sum(), df["v_frag"].sum(), df["v_spare"].sum(), df["v_free"].sum()]
        labs = ["Sistema", "Asignado", "Fragmentación", "Spare", "Libre"]
        cols = [c_sys, c_res, c_frag, c_spare, c_free]

        v_final, l_final, c_final = [], [], []
        total = float(sum(vals))

        for v, l, c in zip(vals, labs, cols):
            if v and v > 0:
                v_final.append(float(v))
                pct = (float(v) / total * 100.0) if total > 0 else 0.0
                l_final.append(f"{l}: {pct:.1f}%")
                c_final.append(c)

        ax.pie(
            v_final,
            labels=l_final,
            colors=c_final,
            wedgeprops=dict(width=0.3),
            textprops={"fontsize": 13},
        )
        ax.set_title(f"Resumen Global - {res}", fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.show()
    print("[plot_fig1_donuts] Plot displayed successfully")


# Sample hardcoded data
sample_data = {
    "vCPU": {
        "df": pd.DataFrame({
            "v_sys": [8, 4, 6],
            "v_res": [32, 24, 28],
            "v_frag": [2, 1, 3],
            "v_spare": [4, 8, 6],
            "v_free": [18, 27, 21],
        })
    },
    "Memoria": {
        "df": pd.DataFrame({
            "v_sys": [16, 8, 12],
            "v_res": [128, 96, 64],
            "v_frag": [8, 4, 6],
            "v_spare": [32, 24, 16],
            "v_free": [72, 124, 158],
        })
    },
    "Disco": {
        "df": pd.DataFrame({
            "v_sys": [50, 30, 40],
            "v_res": [500, 400, 350],
            "v_frag": [25, 15, 20],
            "v_spare": [100, 80, 60],
            "v_free": [325, 475, 530],
        })
    },
}


if __name__ == "__main__":
    print("Generating donut charts with sample data...")
    plot_fig1_donuts(sample_data)
    
    
def run_query(query, variables):

    mat_client = MATClient()
    result = mat_client.graphQL.execute(operation=query, variables=variables)
    if "errors" not in result:
        return result["data"]
    else:
        print(result["errors"])
        return None


# GraphQL query to get cluster metrics
CLUSTER_METRICS_QUERY = """
query get_cluster_data($sites: [String!], $today_minus_two_weeks: timestamptz) {
  Metrics_Cluster_Metrics_Spare_Active(
    where: {_and: [
      {datacenter: {name: {_in: $sites}}}
      {time: {_gt: $today_minus_two_weeks}}
    ]}
    order_by: [{cluster: asc}, {has_vms: desc}, {time: desc}]
    distinct_on: [cluster, has_vms]
  ) {
    cluster
    time
    has_vms
    vcpus
    cpu_cores
    vcpu_flavor
    cpu_fragment_efective
    Memory_GB_hypervisor
    memory_alloc
    mem_reseverd_system
    local_disk_gb
    cpu_spare
    mem_spare
    disk_spare
    disk_reserved
    disk_fragmented
  }
}
"""


def transform_query_to_donut_data(query_result):
    """
    Transform GraphQL query result into the donut chart data structure.
    
    Args:
        query_result: The result from run_query(), expected to have 
                      'Metrics_Cluster_Metrics_Spare_Active' key with list of clusters.
    
    Returns:
        dict: Data structure with vCPU, Memoria, Disco keys, each containing a DataFrame.
    """
    if query_result is None:
        print("Query result is None, returning empty data structure")
        return None
    
    clusters = query_result.get("Metrics_Cluster_Metrics_Spare_Active", [])
    
    if not clusters:
        print("No cluster data found in query result")
        return None
    
    # Initialize lists for each metric
    vcpu_data = {"v_sys": [], "v_res": [], "v_frag": [], "v_spare": [], "v_free": []}
    mem_data = {"v_sys": [], "v_res": [], "v_frag": [], "v_spare": [], "v_free": []}
    disk_data = {"v_sys": [], "v_res": [], "v_frag": [], "v_spare": [], "v_free": []}
    
    for cluster in clusters:
        # === vCPU calculations ===
        vcpu_capacity = cluster.get("vcpus", 0) or 0
        cpu_cores = cluster.get("cpu_cores", 0) or 0  # system/overhead
        cpu_reserved = cluster.get("vcpu_flavor", 0) or 0
        cpu_fragmented = cluster.get("cpu_fragment_efective", 0) or 0
        cpu_spare = cluster.get("cpu_spare", 0) or 0
        
        # Calculate free vCPU
        cpu_used = cpu_cores + cpu_reserved + cpu_fragmented + cpu_spare
        cpu_free = max(0, vcpu_capacity - cpu_used)
        
        vcpu_data["v_sys"].append(cpu_cores)
        vcpu_data["v_res"].append(cpu_reserved)
        vcpu_data["v_frag"].append(cpu_fragmented)
        vcpu_data["v_spare"].append(cpu_spare)
        vcpu_data["v_free"].append(cpu_free)
        
        # === Memoria calculations ===
        mem_capacity = cluster.get("Memory_GB_hypervisor", 0) or 0
        mem_sys = cluster.get("mem_reseverd_system", 0) or 0
        mem_reserved_bytes = cluster.get("memory_alloc", 0) or 0
        mem_reserved = mem_reserved_bytes / (1024**3)  # Bytes to GB
        mem_spare = cluster.get("mem_spare", 0) or 0
        mem_fragmented = 0  # Add if available in query
        
        # Calculate free memory
        mem_used = mem_sys + mem_reserved + mem_fragmented + mem_spare
        mem_free = max(0, mem_capacity - mem_used)
        
        mem_data["v_sys"].append(mem_sys)
        mem_data["v_res"].append(mem_reserved)
        mem_data["v_frag"].append(mem_fragmented)
        mem_data["v_spare"].append(mem_spare)
        mem_data["v_free"].append(mem_free)
        
        # === Disco calculations ===
        disk_capacity = cluster.get("local_disk_gb", 0) or 0
        disk_sys = 0  # System disk overhead if available
        disk_reserved = cluster.get("disk_reserved", 0) or 0
        disk_fragmented = cluster.get("disk_fragmented", 0) or 0
        disk_spare = cluster.get("disk_spare", 0) or 0
        
        # Calculate free disk
        disk_used = disk_sys + disk_reserved + disk_fragmented + disk_spare
        disk_free = max(0, disk_capacity - disk_used)
        
        disk_data["v_sys"].append(disk_sys)
        disk_data["v_res"].append(disk_reserved)
        disk_data["v_frag"].append(disk_fragmented)
        disk_data["v_spare"].append(disk_spare)
        disk_data["v_free"].append(disk_free)
    
    # Build the result structure
    result = {
        "vCPU": {"df": pd.DataFrame(vcpu_data)},
        "Memoria": {"df": pd.DataFrame(mem_data)},
        "Disco": {"df": pd.DataFrame(disk_data)},
    }
    
    return result


def fetch_donut_data(sites, today_minus_two_weeks):
    """
    Fetch cluster metrics and transform to donut chart data structure.
    
    Args:
        sites: List of site/datacenter names to filter by.
        today_minus_two_weeks: Timestamp string for time filter.
    
    Returns:
        dict: Data structure ready for plot_fig1_donuts().
    """
    variables = {
        "sites": sites,
        "today_minus_two_weeks": today_minus_two_weeks
    }
    
    query_result = run_query(CLUSTER_METRICS_QUERY, variables)
    
    if query_result is None:
        return None
    
    return transform_query_to_donut_data(query_result)