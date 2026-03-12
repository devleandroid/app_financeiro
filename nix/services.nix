# services.nix
{ config, lib, pkgs, ... }:

let
  appDir = "/home/lebronx/Documentos/app_financeiro";
  
  # Ambiente Python com todas as dependências
  pythonEnv = pkgs.python313.withPackages (ps: with ps; [
    fastapi
    uvicorn
    streamlit
    requests
    pandas
    numpy
    plotly
    python-dotenv
  ]);
in
{
  # Serviço do Backend FastAPI
  systemd.services.app-financeiro-backend = {
    description = "App Financeiro Backend";
    after = [ "network.target" ];
    wantedBy = [ "multi-user.target" ];
    
    serviceConfig = {
      Type = "simple";
      User = "lebronx";
      WorkingDirectory = appDir;
      Environment = "PYTHONUNBUFFERED=1";
      EnvironmentFile = "${appDir}/.env";
      ExecStart = "${pythonEnv}/bin/uvicorn main:app --host 0.0.0.0 --port 8000";
      Restart = "always";
      RestartSec = 10;
    };
  };

  # Serviço do Frontend Streamlit
  systemd.services.app-financeiro-frontend = {
    description = "App Financeiro Frontend";
    after = [ "network.target" "app-financeiro-backend.service" ];
    wants = [ "app-financeiro-backend.service" ];
    wantedBy = [ "multi-user.target" ];
    
    serviceConfig = {
      Type = "simple";
      User = "lebronx";
      WorkingDirectory = appDir;
      Environment = "PYTHONUNBUFFERED=1";
      EnvironmentFile = "${appDir}/.env";
      ExecStart = "${pythonEnv}/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0";
      Restart = "always";
      RestartSec = 10;
    };
  };

  # Timer para enviar relatório semanal (toda segunda às 9h)
  systemd.timers.app-financeiro-relatorio = {
    description = "Timer para relatório semanal";
    timerConfig = {
      OnCalendar = "Mon *-*-* 09:00:00";
      Persistent = true;
    };
    wantedBy = [ "timers.target" ];
  };

  systemd.services.app-financeiro-relatorio = {
    description = "Envia relatório semanal por email";
    serviceConfig = {
      Type = "oneshot";
      User = "lebronx";
      WorkingDirectory = appDir;
      EnvironmentFile = "${appDir}/.env";
      ExecStart = "${pythonEnv}/bin/python ${appDir}/scripts/enviar_relatorio.py";
    };
  };
}