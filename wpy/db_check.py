#[check MySQL alive using mysqladmin output](gist.github.com/mjbommar/4347285)
#@date 2012-12-20
import smtplib, subprocess, time, sys
from   email.mime.text import MIMEText
sys.path.append('/fs/py/web')
import config.db   as cDB
import config.host as cHO
import config.log  as cLog
import wpy.db      as wDB
import pygame
ODict = wDB.ODict


pygame.init()
#SoundPath = "/home/ubt/.pyenv/versions/py3/lib/python3.6/site-packages/pygame/examples/data/"
#Sound = pygame.mixer.Sound(SoundPath + 'house_lo.wav')
#Sound.play()
MPath      = '/fs/media/audio/soundjax.com/'
#pygame.mixer.music.play()

FillColor = ((255,0,0), (0,255,0), (0,0,255),)
WxH = 800, 600

cLog.VerboseOn = False
WSRep = ODict() # Write-Set Replication API, or wsrep API
SDB = 'SDB'

fromAddress = 'support@wordpy.com'
adminEmail  = 'admin@wordpy.com'

def sendMessage(emailAddress, errorBuffer):
  msg = MIMEText("MySQL down.\nError: " + errorBuffer)
  msg['Subject'] = 'MySQL Down'
  msg['From'] = fromAddress
  msg['To'] = emailAddress
  s = smtplib.SMTP('localhost')
  s.sendmail(fromAddress, emailAddress, msg.as_string())

def main():
  statusProc = subprocess.Popen(['mysqladmin', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  outputBuffer = statusProc.stdout.read().strip()
  errorBuffer = statusProc.stderr.read().strip()

  if 'uptime' not in outputBuffer.lower() or len(errorBuffer) > 0:
    sendMessage(adminEmail, errorBuffer)


# galeracluster.com/documentation-webpages/galerastatusvariables.html
WSRepStatusVars = ODict([       #M: Variables exported by MySQL; Example value
  ('apply_oooe'            , False    ), # 0.671120
  ('apply_oool'            , False    ), # 0.195248
  ('apply_window'          , False    ), # 5.163966
 #('cert_deps_distance'    , False    ), # 23.88889
  ('cert_index_size'       , False    ), # 30936
  ('cert_interval'         , False    ), #
  ('cluster_conf_id'       , False    ),#M 34
  ('cluster_size'          , 3        ),#M 3~5
  ('cluster_state_uuid'    , False    ),#M
  ('cluster_status'        , 'Primary'),#M Primary
  ('commit_oooe'           , False    ), # 0.000000
  ('commit_oool'           , False    ), # 0.000000
  ('commit_window'         , False    ), # 0.000000
  ('connected'             , 'ON'     ), # ON
  ('desync_count'          , False    ), # 0
  ('evs_delayed'           , False    ), #
  ('evs_evict_list'        , False    ), #
  ('evs_repl_latency'      , False    ), #
  ('evs_state'             , False    ), #
 #('flow_control_paused'   , False    ), # 0.184353
  ('flow_control_paused_ns', False    ), # 20222491180
  ('flow_control_recv'     , False    ), # 11
  ('flow_control_sent'     , False    ), # 7
  ('gcomm_uuid'            , False    ), #
  ('incoming_addresses'    , False    ), #
  ('last_committed'        , False    ), # 409745
  ('local_bf_aborts'       , False    ), # 960
  ('local_cached_downto'   , False    ), #
  ('local_cert_failures'   , False    ), # 333
  ('local_commits'         , False    ), # 14981
  ('local_index'           , False    ), # 1
  ('local_recv_queue'      , False    ), # 0
 #('local_recv_queue_avg'  , False    ), # 3.348452
  ('local_recv_queue_max'  , False    ), # 10
  ('local_recv_queue_min'  , False    ), # 0
  ('local_replays'         , False    ), # 0
  ('local_send_queue'      , False    ), # 1
 #('local_send_queue_avg'  , False    ), # 0.145000
  ('local_send_queue_max'  , False    ), # 10
  ('local_send_queue_min'  , False    ), # 0
  ('local_state'           , False    ), # 4
  ('local_state_comment'   , ('Synced', 'Donor/Desynced',
                              'Joining: receiving State Transfer',) ), # Synced
  ('local_state_uuid'      , False    ), #
  ('protocol_version'      , False    ), # 4
  ('provider_name'         , False    ),#M Galera
  ('provider_vendor'       , False    ),#M
  ('provider_version'      , False    ),#M
  ('ready'                 , 'ON'     ),#M ON
  ('received'              , False    ), # 17831
  ('received_bytes'        , False    ), # 6637093
  ('repl_data_bytes'       , False    ), # 265035226
  ('repl_keys'             , False    ), # 797399
  ('repl_keys_bytes'       , False    ), # 11203721
  ('repl_other_bytes'      , False    ), # 0
  ('replicated'            , False    ), # 16109
  ('replicated_bytes'      , False    ), # 6526788
  ('local_recv_queue_avg'  , True     ), # 3.348452
  ('flow_control_paused'   , True     ), # 0.184353
  ('cert_deps_distance'    , True     ), # 23.8889
  ('local_send_queue_avg'  , True     ), # 0.145000
])


def AllHosts(DbHosts, SId=1):
  Host_0_Ok = False
  Host0 = DbHosts[0]
  for  i, Host in enumerate(DbHosts):
    Host_i_Ok = True
    print("\n{:6} WSRepStatus: ExpectedVal == CurrentVal is T/F".format(Host))
    #if Host == cHO.H000002:
    #  continue
    if Host not in WSRep:
      WSRep[Host] = ODict()
    if SDB not in WSRep[Host]:
      WSRep[Host][SDB] = wDB.SiteDbCls(SId, DbHost=Host, ConnSsh=True)

    for Status,Expected in WSRepStatusVars.items():
      if not Expected:
        continue
      Sql = "SHOW STATUS LIKE '{}'".format('wsrep_' + Status)
      Res = WSRep[Host][SDB].Exec(Sql, Action='fetchone', Tries=2)
      if not Res:
        #PauseAlert()
        Host_i_Ok = False
        break
      WSRepStatus = Res['Value']
      if Status == 'cluster_size':
        WSRepStatus = int(WSRepStatus)
        if Host in cHO.GDbHs_WpPub:
          Expected = 5
      WSRep[Host][Status] = WSRepStatus
      if Expected is True:
        print("  {:20}: {}".format(Status, WSRepStatus))
        continue
      if not isinstance(Expected, (tuple, list)):
        Expected = (Expected,)

      # If Status = ready and local_state_comment == 'Joining...'
      #   WSRepStatusOk is True even though WSRepStatus could be OFF
      WSRepStatusOk = True if (Status == 'ready' and
                               WSRep[Host].get('local_state_comment','' )
                               == 'Joining: receiving State Transfer'
                           ) else WSRepStatus in Expected   #Old: == Expected

      print("  {:20}: {:<8} in Expected is {}".format(
            Status, WSRepStatus, WSRepStatusOk))
      if Status != 'cluster_size' and not WSRepStatusOk:
        Host_i_Ok = False
        SoundAlert()

    print('ALL UP!' if Host_i_Ok else 'DOWN!!')
    if Host_i_Ok and (WSRep[Host]['cluster_status']      == 'non-Primary' or
                      WSRep[Host]['local_state_comment'] == 'Initialized'):
      PauseAlert()

    if i == 0:
      if Host_i_Ok:
        Host_0_Ok = True
      else:
        SoundAlert()
      continue
    #if i > 0:  # else:
    if Host_i_Ok:
      continue
    if Host_0_Ok:
      Out, Err = WSRep[Host][SDB].DbH.ServiceStatus('mysql')
      if Out is False:
        SoundAlert()
      elif 'Active: failed' in Out or 'Active: inactive (dead)' in Out:
        WSRep[Host][SDB].DbH.ServiceRestart('mysql')
      elif 'Active: activating (start)' in Out:
        pass
      else:
        SoundAlert()
      continue
    #else:
    Out_i, Err_i = WSRep[Host ][SDB].DbH.ServiceForceStop('mysql')
    Out_0, Err_0 = WSRep[Host0][SDB].DbH.ServiceForceStop('mysql')
    if ((Out_i is False and Err_i is False) or
        (Out_0 is False and Err_0 is False)   ):
      PauseAlert()
    #vi /etc/systemd/system/mysql.service
    # _WSREP_NEW_CLUSTER is for the exclusive use of galera_new_cluster script
    #ExecStart=/usr/sbin/mysqld $MYSQLD_OPTS $_WSREP_NEW_CLUSTER \
    #                           $_WSREP_START_POSITI ON
    Out_0_Env0, Err_0_Env0 = WSRep[Host0][SDB].DbH.Exec(
                           'export _WSREP_NEW_CLUSTER="--wsrep-new-cluster"')
    Out_0, Err_0 = WSRep[Host0][SDB].DbH.ServiceStart('mysql')
    Out_0_Env1, Err_0_Env1 = WSRep[Host0][SDB].DbH.Exec(
                           'export _WSREP_NEW_CLUSTER=""')
    time.sleep(10)
    Out_0_Status, Err_0_Status = WSRep[Host0][SDB].DbH.ServiceStatus('mysql')
    if not 'Active: active (running)' in Out_0_Status:
      SoundAlert()
    #elif 'Active: failed' in Out_0_Status:
    #  WSRep[Host][SDB].DbH.ServiceRestart('mysql')
    #elif 'Active: activating (start)' in Out_0_Status:
    #  pass
    Out_i, Err_i = WSRep[Host ][SDB].DbH.ServiceStart('mysql')

  print('\n')
  #pprint(WSRep)

#   #[ODict([('Variable_name','wsrep_local_state_comment'),('Value','Synced')])]
#   print(SDB.Exec("SHOW STATUS LIKE 'wsrep_local_state_comment'"))
#   # 'Synced' = node is connected to the cluster and operational.
#   # Joining, Waiting on SST, Joined, Synced or Donor
#   #          = node is part of Primary Component
#   # 'Initialized' = node is part of a nonoperational component
#   print(SDB.Exec("SHOW STATUS LIKE 'wsrep_cluster_size'"))
#   # wsrep_cluster_size = the nodes in the cluster
#   print(SDB.Exec("SHOW STATUS LIKE 'wsrep_ready'"))
#   # wsrep_ready ON = node connected to cluster, able to handle transactions
#   # ON: can accept write-sets from the cluster. OFF: almost all queries fail
#   print(SDB.Exec("SHOW STATUS LIKE 'wsrep_cluster_status'"))
#   # status = Primary, or else the node is part of a nonoperational component.
#   #   multiple membership changes cause loss of quorum, split-brain situations
#   print(SDB.Exec("SHOW STATUS LIKE 'wsrep_connected'"))
#   # if the node has network connectivity with any other nodes



def SoundAlert(MusicFile = '24448^down.mp3'):
  " SoundAlert(MusicFile = '70640-shutdown.mp3')  "
  pygame.mixer.music.load(MPath + MusicFile)
  pygame.mixer.music.play()

def PauseAlert():
  running = True
  i = 0
  screen = pygame.display.set_mode((WxH))

  while running:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = False
    screen.fill(FillColor[ i%3 ] )
    pygame.display.flip()
    SoundAlert(MusicFile = '70640-shutdown.mp3')
    time.sleep(2)
    i += 1

if __name__ == "__main__":
  #AllHosts(cHO.GDbHs_WpPub, SId=1)
  #AllHosts(cHO.WDbHsDC0000 , SId=5)
  while True:
    for SId, Hosts in cDB.SIdDbHosts.items():
      AllHosts(Hosts, SId=SId)
      time.sleep(120)
  #main()


'''
wsrep_cluster_address="gcomm://"
wsrep_cluster_address="gcomm://web1,db1,db2"

vi /etc/systemd/system/mysql.service
# MYSQLD_OPTS here is for users to set in /etc/systemd/system/mariadb.service.d/MY_SPECIAL.conf
# Use the [service] section and Environment="MYSQLD_OPTS=...".
# This isn't a replacement for my.cnf.
# _WSREP_NEW_CLUSTER is for the exclusive use of the script galera_new_cluster
ExecStart=/usr/sbin/mysqld $MYSQLD_OPTS $_WSREP_NEW_CLUSTER $_WSREP_START_POSITI ON


 galeracluster.com/documentation-webpages/testingcluster.html
 To test that Galera Cluster is working as expected, complete the following steps:
 On the database client, verify that all nodes have connected to each other:
     SHOW STATUS LIKE 'wsrep_%';
      | Variable_name             | Value      |
      | wsrep_local_state_comment | Synced (6) |
      | wsrep_cluster_size        | 3          |
      | wsrep_ready               | ON         |
 * wsrep_local_state_comment: The value Synced indicates that the node is connected to the cluster and operational.
 * wsrep_cluster_size: The value indicates the nodes in the cluster.
 * wsrep_ready: The value ON indicates that this node is connected to the cluster and able to handle transactions.

 Split-brain Testing
 To test Galera Cluster for split-brain situations on a two node cluster, complete the following steps:
     Disconnect the network connection between the two cluster nodes.
     The quorum is lost and the nodes do not serve requests.
     Reconnect the network connection.
     The quorum remains lost, and the nodes do not serve requests.
     On one of the database clients, reset the quorum:
     SET GLOBAL wsrep_provider_options='pc.bootstrap=1';
 The quorum is reset and the cluster recovered.




galeracluster.com/documentation-webpages/monitoringthecluster.html

Checking Cluster Integrity
--------------------------
 check cluster integrity using the following status variables:
    wsrep_cluster_state_uuid shows the cluster state UUID, which you can use to determine whether the node is part of the cluster.
    SHOW GLOBAL STATUS LIKE 'wsrep_cluster_state_uuid';
    | Variable_name            | Value                                |
    | wsrep_cluster_state_uuid | d6a51a3a-b378-11e4-924b-23b6ec126a13 |
    Each node in the cluster should provide the same value. When a node carries a different value, this indicates that it is no longer connected to rest of the cluster. Once the node reestablishes connectivity, it realigns itself with the other nodes.

    wsrep_cluster_conf_id shows the total number of cluster changes that have happened, which you can use to determine whether or not the node is a part of the Primary Component.
    SHOW GLOBAL STATUS LIKE 'wsrep_cluster_conf_id';
    | Variable_name         | Value |
    | wsrep_cluster_conf_id | 32    |
    Each node in the cluster should provide the same value. When a node carries a different, this indicates that the cluster is partitioned. Once the node reestablish network connectivity, the value aligns itself with the others.

    wsrep_cluster_size shows the number of nodes in the cluster, which you can use to determine if any are missing.
    SHOW GLOBAL STATUS LIKE 'wsrep_cluster_size';
    | Variable_name      | Value |
    | wsrep_cluster_size | 15    |
    You can run this check on any node. When the check returns a value lower than the number of nodes in your cluster, it means that some nodes have lost network connectivity or they have failed.

    wsrep_cluster_status shows the primary status of the cluster component that the node is in, which you can use in determining whether your cluster is experiencing a partition.
    SHOW GLOBAL STATUS LIKE 'wsrep_cluster_status';
    | Variable_name        | Value   |
    | wsrep_cluster_status | Primary |
    The node should only return a value of Primary. Any other value indicates that the node is part of a nonoperational component. This occurs in cases of multiple membership changes that result in a loss of quorum or in cases of split-brain situations.
    In the event that you check all nodes in your cluster and find none that return a value of Primary, see Resetting the Quorum.

When these status variables check out and return the desired results on each node, the cluster is up and has integrity. What this means is that replication is able to occur normally on every node. The next step then is checking node status to ensure that they are all in working order and able to receive write-sets.

Checking the Node Status
------------------------
In addition to checking cluster integrity, you can also monitor the status of individual nodes. This shows whether nodes receive and process updates from the cluster write-sets and can indicate problems that may prevent replication.
    wsrep_ready shows whether the node can accept queries.
    SHOW GLOBAL STATUS LIKE 'wsrep_ready';
    | Variable_name | Value |
    | wsrep_ready   | ON    |
    When the node returns a value of ON it can accept write-sets from the cluster. When it returns the value OFF, almost all queries fail with the error:
    ERROR 1047 (08501) Unknown Command

    wsrep_connected shows whether the node has network connectivity with any other nodes.
    SHOW GLOBAL STATUS LIKE 'wsrep_connected';
    | Variable_name   | Value |
    | wsrep_connected | ON    |
    When the value is ON, the node has a network connection to one or more other nodes forming a cluster component. When the value is OFF, the node does not have a connection to any cluster components.
    Note
    The reason for a loss of connectivity can also relate to misconfiguration. For instance, if the node uses invalid values for the wsrep_cluster_address or wsrep_cluster_name parameters.
    Check the error log for proper diagnostics.

    wsrep_local_state_comment shows the node state in a human readable format.
    SHOW GLOBAL STATUS LIKE 'wsrep_local_state_comment';
    | Variable_name             | Value  |
    | wsrep_local_state_comment | Joined |
    When the node is part of the Primary Component, the typical return values are Joining, Waiting on SST, Joined, Synced or Donor. In the event that the node is part of a nonoperational component, the return value is Initialized.

    Note
    If the node returns any value other than the one listed here, the state comment is momentary and transient. Check the status variable again for an update.
In the event that each status variable returns the desired values, the node is in working order. This means that it is receiving write-sets from the cluster and replicating them to tables in the local database.

Checking the Replication Health
-------------------------------
Monitoring cluster integrity and node status can show you issues that may prevent or otherwise block replication. These status variables will help in identifying performance issues and identifying problem areas so that you can get the most from your cluster.
Note
Unlike other the status variables, these are differential and reset on every FLUSH STATUS command.
Galera Cluster triggers a feedback mechanism called Flow Control to manage the replication process. When the local received queue of write-sets exceeds a certain threshold, the node engages Flow Control to pause replication while it catches up.
You can monitor the local received queue and Flow Control using the following status variables:

    wsrep_local_recv_queue_avg shows the average size of the local received queue since the last status query.
    SHOW STATUS LIKE 'wsrep_local_recv_queue_avg';
    | Variable_name            | Value    |
    | wsrep_local_recv_que_avg | 3.348452 |
    When the node returns a value higher than 0.0 it means that the node cannot apply write-sets as fast as it receives them, which can lead to replication throttling.
    Note
    In addition to this status variable, you can also use wsrep_local_recv_queue_max and wsrep_local_recv_queue_min to see the maximum and minimum sizes the node recorded for the local received queue.

    wsrep_flow_control_paused shows the fraction of the time, since FLUSH STATUS was last called, that the node paused due to Flow Control.
    SHOW STATUS LIKE 'wsrep_flow_control_paused';
    | Variable_name             | Value    |
    | wsrep_flow_control_paused | 0.184353 |
    When the node returns a value of 0.0, it indicates that the node did not pause due to Flow Control during this period. When the node returns a value of 1.0, it indicates that the node spent the entire period paused. If the time between FLUSH STATUS and SHOW STATUS was one minute and the node returned 0.25, it indicates that the node was paused for a total 15 seconds over that time period.
    Ideally, the return value should stay as close to 0.0 as possible, since this means the node is not falling behind the cluster. In the event that you find that the node is pausing frequently, you can adjust the wsrep_slave_threads parameter or you can exclude the node from the cluster.

    wsrep_cert_deps_distance shows the average distance between the lowest and highest sequence number, or seqno, values that the node can possibly apply in parallel.
    SHOW STATUS LIKE 'wsrep_cert_deps_distance';
    | Variable_name            | Value   |
    | wsrep_cert_deps_distance | 23.8889 |
    This represents the node’s potential degree for parallelization. In other words, the optimal value you can use with the wsrep_slave_threads parameter, given that there is no reason to assign more slave threads than transactions you can apply in parallel.

Detecting Slow Network Issues
-------------------------------
While checking the status of Flow Control and the received queue can tell you how the database server copes with incoming write-sets, you can check the send queue to monitor for outgoing connectivity issues.
Note
Unlike other the status variables, these are differential and reset on every FLUSH STATUS command.

wsrep_local_send_queue_avg show an average for the send queue length since the last FLUSH STATUS query.
SHOW STATUS LIKE 'wsrep_local_send_queue_avg';
| Variable_name              | Value    |
| wsrep_local_send_queue_avg | 0.145000 |
Values much greater than 0.0 indicate replication throttling or network throughput issues, such as a bottleneck on the network link. The problem can occur at any layer from the physical components of your server to the configuration of the operating system.
Note
In addition to this status variable, you can also use wsrep_local_send_queue_max and wsrep_local_send_queue_min to see the maximum and minimum sizes the node recorded for the local send queue.



http://galeracluster.com/documentation-webpages/quorumreset.html

Finding the Most Advanced Node
------------------------------
Before you can reset the quorum, you need to identify the most advanced node in the cluster. That is, you must find the node whose local database committed the last transaction. Regardless of the method you use in resetting the quorum, this node serves as the starting point for the new Primary Component.
Identifying the most advanced node in the cluster requires that you find the node with the most advanced sequence number, or seqno. You can determine this using the wsrep_last_committed status variable.
From the database client on each node, run the following query:
  SHOW STATUS LIKE 'wsrep_last_committed';
  | Variable_name        | Value  |
  | wsrep_last_committed | 409745 |
The return value is the seqno for the last transaction the node committed. The node that provides the highest seqno is the most advanced node in your cluster. Use it as the starting point in the next section when bootstrapping the new Primary Component.

Resetting the Quorum
--------------------
When you reset the quorum what you are doing is bootstrapping the Primary Component on the most advanced node you have available. This node then functions as the new Primary Component, bringing the rest of the cluster into line with its state.
There are two methods available to you in this process: automatic and manual.
Note
The preferred method for a quorum reset is the automatic method. Unlike the manual method, automatic bootstraps preserve the write-set cache, or GCache, on each node. What this means is that when the new Primary Component starts, some or all of the joining nodes can provision themselves using the Incremental State Transfer (IST) method, rather than the much slower State Snapshot Transfer (SST) method.

Automatic Bootstrap
--------------------
Resetting the quorum bootstraps the Primary Component onto the most advanced node. In the automatic method this is done by enabling pc.bootstrap under wsrep_provider_options dynamically through the database client. This makes the node a new Primary Component.
To perform an automatic bootstrap, on the database client of the most advanced node, run the following command:
SET GLOBAL wsrep_provider_options='pc.bootstrap=YES';
The node now operates as the starting node in a new Primary Component. Nodes in nonoperational components that have network connectivity attempt to initiate incremental state transfers if possible, state snapshot transfers if not, with this node, bringing their own databases up-to-date.

Manual Bootstrap
Resetting the quorum bootstraps the Primary Component onto the most advanced node. In the manual method this is done by shutting down the cluster, then starting it up again beginning with the most advanced node.
To manually bootstrap your cluster, complete the following steps:
    systemctl stop mysql                      # Shut down all cluster nodes
    systemctl start mysql --wsrep-new-cluster # Start the most advanced node
    systemctl start mysql                     # Start other nodes in cluster
When the first node starts with the --wsrep-new-cluster option, it initializes a new cluster using the data from the most advanced state available from the previous cluster. As the other nodes start they connect to this node and request state snapshot transfers, to bring their own databases up-to-date.


ps -ef | grep mysql
mysql    56542 56529  0 13:33 ?        00:00:00 sh -c wsrep_sst_rsync --role 'joiner' --address '10.1.1.5' --auth '' --datadir '/fs/mysql/' --defaults-file '/etc/mysql/my.cnf' --defaults-group-suffix '' --parent '56529' --binlog '/var/log/mysql/mariadb-bin'
mysql    56543 56542  0 13:33 ?        00:00:00 /bin/bash -ue /usr//bin/wsrep_sst_rsync --role joiner --address 10.1.1.5 --auth  --datadir /fs/mysql/ --defaults-file /etc/mysql/my.cnf --defaults-group-suffix  --parent 56529 --binlog /var/log/mysql/mariadb-bin
mysql    56582 56543  0 13:33 ?        00:00:00 rsync --daemon --no-detach --port 4444 --config /fs/mysql//rsync_sst.conf


'''


