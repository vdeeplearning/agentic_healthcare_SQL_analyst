"""Project command line interface."""
import argparse,json
from src.config import get_settings
from src.database.seed import generate_database
from src.evaluation.evaluator import run_benchmark
def main():
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="command",required=True)
    seed=sub.add_parser("seed"); seed.add_argument("--patients",type=int,default=25_000); seed.add_argument("--encounters",type=int,default=100_000); seed.add_argument("--seed",type=int,default=42)
    bench=sub.add_parser("benchmark"); bench.add_argument("--limit",type=int,default=None)
    args=parser.parse_args(); settings=get_settings()
    if args.command=="seed": print(generate_database(settings.db_path,args.seed,args.patients,args.encounters))
    else: print(json.dumps(run_benchmark(settings.db_path,args.limit),indent=2))
if __name__=="__main__": main()
