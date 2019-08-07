import sys
import wake

if __name__ == '__main__':
    try:
        wake.main(sys.argv)
    except:
        if wake.MODE == wake.DEBUG:
            import traceback, pdb
            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)
        else:
            raise


