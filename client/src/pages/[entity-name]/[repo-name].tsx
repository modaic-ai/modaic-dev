import React from 'react'
import { useRouter } from 'next/router'

function Index() {
  const router = useRouter();
  const { entityName, repoName } = router.query;

  return (
    <div>Index {entityName} {repoName}</div>
  )
}

export default Index