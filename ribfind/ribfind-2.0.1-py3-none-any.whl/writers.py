import os
import colorsys
from jinja2 import Template


class TemplateWriter:
    """A writer for Jinja2 templates."""

    def __init__(self, template, output_file):
        this_dir, this_filename = os.path.split(__file__)
        template_path = os.path.join(
            this_dir,
            ".",
            "template",
            template
        )

        with open(template_path, encoding="utf8") as template_file:
            self.template = Template(template_file.read())
            self.output_file = output_file

    def render(self):
        return self.template.render(data=self)

    def write(self, directory):
        output_file = f"{directory}/{self.output_file}"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf8") as out:
            out.write(self.render())


class ChimeraxWriter(TemplateWriter):
    """Generates ChimeraX scripts for coloring clusters"""

    def __init__(self, contact_dist, clusters, model):
        output_file = f"chimerax_{(clusters.edge_cutoff * 100):.2f}.cxc"
        super().__init__("chimerax.txt", output_file)
        self.clusters = clusters
        self.contact_dist = contact_dist
        self.saturation = 0.5
        self.value = 0.5
        self.model = model

    def cluster_colors(self):
        return zip(self._atomspecs(), self._colors())

    def _colors(self):
        """Returns a list of colors for the clusters"""
        num_clusters = len(self.clusters.dens_clusters())
        hues = [float(x) / num_clusters for x in range(num_clusters)]
        hsvs = [(h, self.saturation, self.value) for h in hues]
        hexs = []
        for hsv in hsvs:
            (red, green, blue) = [int(c * 255) for c in colorsys.hsv_to_rgb(*hsv)]
            hex_code = f"#{red:02x}{green:02x}{blue:02x}"
            hexs.append(hex_code)
        return hexs

    def _atomspec(self, cluster):
        """Returns atomspecs for each cluster"""
        contigs = []
        for contig in cluster.get_contigs():
            contigs.append(f"#1/{contig.chain_id}:{contig.start}-{contig.stop-1}")
        spec = " ".join(contigs)
        return spec

    def _atomspecs(self):
        return [self._atomspec(cluster) for cluster in self.clusters.dens_clusters()]


class RigidBodyWriter(TemplateWriter):
    """Generates rigid body files."""

    def __init__(self, contact_dist, clusters):
        output_file = f"rigid_body_{(clusters.edge_cutoff * 100):.2f}.txt"
        super().__init__("rigid_body.txt", output_file)
        self.clusters = clusters
        self.contact_dist = contact_dist


class SummaryWriter(TemplateWriter):
    def __init__(self, solutions):
        super().__init__("summary.txt", "summary.txt")
        self.solutions = solutions


class Writer:
    def __init__(self, path, model, contact_dist):
        self.path = path
        self.contact_dist = contact_dist
        self.model = model

    def write(self, solutions):
        summary = SummaryWriter(solutions)
        print(summary.render())
        print(f"Writing RIBFIND files to {self.path}/")
        for solution in solutions:
            rb_writer = RigidBodyWriter(self.contact_dist, solution)
            rb_writer.write(self.path)
        print(f"Writing ChimeraX scripts to {self.path}/")
        for solution in solutions:
            chimerax = ChimeraxWriter(self.contact_dist, solution, self.model)
            chimerax.write(self.path)
