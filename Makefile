docker_build_local:
	docker build -t minyma:latest .

docker_build_release_dev:
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t gitea.va.reichard.io/evan/minyma:dev \
		--push .

docker_build_release_latest:
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t gitea.va.reichard.io/evan/minyma:latest \
		-t gitea.va.reichard.io/evan/minyma:`git describe --tags` \
		--push .
