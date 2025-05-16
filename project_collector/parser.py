import argparse

def get_user_args():
    """Get all arguments from command line."""
    parser = argparse.ArgumentParser(
        description="Project Collector: coleta conteúdo e exibe árvore de diretórios"
    )
    parser.add_argument(
        'directory',
        help='Diretório raiz para processar'
    )
    parser.add_argument(
        '--no-defaults',
        action='store_true',
        help='Ignorar padrões de ignore definidos em config_defaults.json'
    )
    parser.add_argument(
        '--only-tree',
        action='store_true',
        help='Exibir apenas a árvore de diretórios'
    )
    parser.add_argument(
        '--project', '-p',
        required=True,
        help='Nome do conjunto de configs a usar (ex: project_x)'
    )
    parser.add_argument(
        '--output', '-o',
        default='output.txt',
        help='Arquivo de saída (padrão: output.txt)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verboso para debug'
    )
    return parser.parse_args()