set -e

cudaid=$1
dname=$2
gnn=$3
lr=$4
local_update=$5

if [[ $dname = 'mol' ]]; then
    dataset='graph_multi_domain_mol'
elif [[ $dname = 'mix' ]]; then
    dataset='graph_multi_domain_mix'
elif [[ $dname = 'biochem' ]]; then
    dataset='graph_multi_domain_biochem'
elif [[ $dname = 'v1' ]]; then
    dataset='graph_multi_domain_kddcupv1'
else
    dataset='graph_multi_domain_small'
fi

if [ ! -d "out" ];then
  mkdir out
fi

out_channels=0
hidden=64
splitter='ooxx'

echo "HPO starts..."

lr_servers=(0.5 0.1)

for (( s=0; s<${#lr_servers[@]}; s++ ))
do
    for k in {1..5}
    do
        python federatedscope/main.py --cfg federatedscope/gfl/baseline/fedavg_gnn_minibatch_on_multi_task.yaml device ${cudaid} data.type ${dataset} data.splitter ${splitter} optimizer.lr ${lr} federate.local_update_steps ${local_update} model.type ${gnn} model.out_channels ${out_channels} model.hidden ${hidden} seed $k federate.method FedOpt fedopt.optimizer.lr ${lr_servers[$s]} >>out/${gnn}_${lr}_${local_update}_on_${dataset}_${splitter}_${lr_servers[$s]}_opt.log 2>&1
    done
done

for (( s=0; s<${#lr_servers[@]}; s++ ))
do
    python federatedscope/parse_exp_results.py --input out/${gnn}_${lr}_${local_update}_on_${dataset}_${splitter}_${lr_servers[$s]}_opt.log >>out/final_${gnn}_${lr}_${local_update}_on_${dataset}_${splitter}_opt.out 2>&1
done

echo "HPO ends."
