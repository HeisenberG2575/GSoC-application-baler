
def set_config(c):
    c.input_path          = "data/aditya/aditya.pickle"
    c.path_before_pre_processing = "data/aditya/MultiJetRun2010B.csv"
    c.compression_ratio   = 2.0
    c.epochs              = 10
    c.early_stopping      = True
    c.lr_scheduler        = True
    c.patience            = 8
    c.min_delta           = 0.00005
    c.model_name          = "VarAutoEnc"
    c.custom_norm         = False
    c.l1                  = True
    c.reg_param           = 0.001
    c.RHO                 = 0.05
    c.lr                  = 0.0001
    c.batch_size          = 64
    c.save_as_root        = True
    c.test_size           = 0.15
    c.vae                 = True
