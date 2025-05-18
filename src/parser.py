import argparse
from pathlib import Path

def get_user_args():
    """
    Configura o CLI para:
        - Gerenciar config persistente (--config, --set-config, --clear-config, --show-config)
        - Processar diretório opcional (posicional)
        - Flags de execução (no_defaults, only_tree, verbose)

    Retorna:
        Namespace com atributos:
            directory: Path | None
            config: str | None
            set_config: str | None
            clear_config: bool
            show_config: bool
            no_defaults: bool
            only_tree: bool
            verbose: bool
    """
    parser = argparse.ArgumentParser(
        prog='projcol',
        description='Project Collector: coleta conteúdo e exibe árvore de diretórios'
    )
    # Diretório alvo: opcional para comandos de gerenciamento
    parser.add_argument(
        'directory',
        nargs='?',  # opcional
        type=lambda p: Path(p).expanduser(),
        help='Diretório raiz para processar (use "." para cwd ou caminho relativo)'
    )

    # Grupo para gerenciar config persistente
    group = parser.add_mutually_exclusive_group()
    # override temporário para esta execução
    group.add_argument(
        '--use-config', '--ucfg',
        dest='use_config',
        metavar='CONFIG',
        help='Config temporário para esta execução (sobrescreve o padrão)'
    )
    # define config padrão
    group.add_argument(
        '--set-config', '--scfg',
        dest='set_config',
        metavar='CONFIG',
        help='Define CONFIG como padrão para futuras execuções'
    )
    # limpa config padrão
    group.add_argument(
        '--clear-config', '--ccfg',
        action='store_true',
        dest='clear_config',
        help='Limpa o config padrão, voltando ao estado sem padrão'
    )
    # mostra config padrão
    group.add_argument(
        '--get-config', '--gcfg',
        action='store_true',
        dest='get_config',
        help='Mostra o config padrão atualmente definido'
    )
    group.add_argument(
        '--list-configs', '-lcfg',
        action='store_true',
        dest='list_configs',
        help='Lista todos os configs disponíveis'
    )

    # Flags de execução do collector
    parser.add_argument(
        '--no-defaults',
        action='store_true',
        help='Ignorar defaults ao carregar config'
    )
    parser.add_argument(
        '--only-tree',
        action='store_true',
        help='Gerar apenas árvore sem coletar conteúdo'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verboso para debug'
    )

    return parser.parse_args()
