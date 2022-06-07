import logging
import uuid

from beamngpy import StaticObject

from sdc_scissor.obstacle_api.tree import Tree


class BeamngTree(Tree):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self):
        name = uuid.uuid4().hex[:3].upper()
        name = "pyTree_" + name

        return StaticObject(
            name=name,
            pos=(self.x_pos, self.y_pos, self.z_pos),
            rot=self.rot,
            rot_quat=self.rot_quat,
            scale=(0.25, 0.25, 0.25),
            shape="/levels/west_coast_usa/art/shapes/trees/trees_conifer/BBZ_redwood1.dae",
        )


if __name__ == "__main__":
    logging.info("beamng_tree.py")
