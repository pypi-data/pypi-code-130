import torch

from zeroml.dl.losses import ArcFaceLoss, ArcMarginProduct


def test_arc_face_loss():

    NUM_CLASSES = 2
    BS = 256
    FEATURE_SIZE = 512
    target = torch.empty(BS, dtype=torch.long).random_(NUM_CLASSES)

    margin_product = ArcMarginProduct(FEATURE_SIZE, NUM_CLASSES)
    arc_loss = ArcFaceLoss()

    features = torch.randn(BS, FEATURE_SIZE)
    logits = margin_product(features)

    loss = arc_loss.forward(logits, target)
    loss.backward()
