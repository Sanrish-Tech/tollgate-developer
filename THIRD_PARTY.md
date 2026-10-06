# Third-party components

The proprietary Developer distribution terms do not replace component licences.
Images retain installed Python package metadata and upstream notices.

- TollGate Community base: Apache-2.0; licence and original notice in licenses/.
- Redis 7.4.11: Redis dual licensing; RSALv2 terms are included in licenses/Redis-7.4.11-LICENSE.txt. Redis is used as an internal component, with no exposed Redis service. Source: https://github.com/redis/redis/tree/7.4.11 .
- LiteLLM identity gateway: upstream licence in licenses/LiteLLM-LICENSE.txt. Enterprise features are not enabled. Original upstream source: https://github.com/BerriAI/litellm . Its image includes its own component notices; those govern any included enterprise components.
- PostgreSQL 16: https://www.postgresql.org/about/licence/ .
- Python: https://docs.python.org/3/license.html .
- Alpine and Python dependencies: retain their original notices in each image. The release manifest identifies exact image digests.

Redis and PostgreSQL container operating-system packages were upgraded; PostgreSQL's entrypoint uses su-exec in place of gosu. LiteLLM's operating-system packages and tornado, pypdf, anyio and PyJWT were updated; its routing configuration is identity-only. These changes are made by Sanrish, not upstream endorsements.

Provider APIs are external services with separate terms and charges. No provider credentials or private signing keys are included.
