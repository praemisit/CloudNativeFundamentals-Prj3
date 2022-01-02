# Instructions provided by https://www.jaegertracing.io/docs/1.29/operator/
kubectl create namespace observability

# Add an ingress to cluster
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.1.0/deploy/static/provider/cloud/deploy.yaml

# Wait to let the ingress service get started
echo "Waiting for 15 seconds to let ingress service starting"
sleep 15s

# Install the jaeger operator
kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.29.0/jaeger-operator.yaml -n observability

# Wait to let the ingress service get started
echo "Waiting for 15 seconds to let the jaeger operator starting"
sleep 15s

# Once the Jaeger Operator is ready, install the jaeger instance
# https://github.com/jaegertracing/jaeger-operator#getting-started
kubectl apply -n observability -f - <<EOF
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: simplest
EOF

# Check the availability
kubectl get -n observability ingress