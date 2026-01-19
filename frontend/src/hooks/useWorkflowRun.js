import { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';

export const useWorkflowRun = () => {
  const [isRunning, setIsRunning] = useState(false);

  const executeWorkflow = useCallback(async ({ nodes, edges, setNodes, nodeIds = null }) => {
    if (isRunning) return;

    // Normalize nodeIds: if it's not an array (e.g. MouseEvent), treat as null (run all)
    const runNodeIds = Array.isArray(nodeIds) ? nodeIds : null;

    setIsRunning(true);

    // Reset status and results for nodes being run
    setNodes((nds) =>
      nds.map((node) => {
        const shouldRun = !runNodeIds || (Array.isArray(runNodeIds) && runNodeIds.includes(node.id));
        if (shouldRun) {
          return {
            ...node,
            data: { ...node.data, status: 'idle', executionResult: null },
          };
        }
        return node;
      })
    );

    try {
      const response = await fetch('/api/workflow/execute/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow: {
            id: "workflow-" + uuidv4(),
            name: "Untitled Workflow",
            nodes: nodes.map(n => ({
              id: n.id,
              type: n.type,
              position: n.position,
              data: {
                ...n.data,
                value: n.data.value
              }
            })),
            edges: edges.map(e => ({
              id: e.id,
              source: e.source,
              target: e.target,
              sourceHandle: e.sourceHandle,
              targetHandle: e.targetHandle
            }))
          },
          node_ids: runNodeIds,
        }),
      });

      if (!response.ok) throw new Error(`Execution failed: ${response.statusText}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop(); // Keep incomplete chunk

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (!trimmedLine || !trimmedLine.startsWith('data: ')) continue;

          try {
            const dataStr = trimmedLine.slice(6);
            if (dataStr === '[DONE]') break;

            const data = JSON.parse(dataStr);

            if (data.type === 'node_started') {
              setNodes((nds) =>
                nds.map((n) =>
                  n.id === data.node_id
                    ? { ...n, data: { ...n.data, status: 'running' } }
                    : n
                )
              );
            } else if (data.type === 'node_completed' || data.type === 'node_failed') {
              setNodes((nds) =>
                nds.map((n) =>
                  n.id === data.node_id
                    ? {
                      ...n,
                      data: {
                        ...n.data,
                        status: data.type === 'node_completed' ? 'completed' : 'failed',
                        executionResult: data.result,
                      },
                    }
                    : n
                )
              );
            } else if (data.type === 'workflow_completed') {
              // We will set isRunning false at the end of the function anyway/or catch
              // but strictly speaking we should just wait for loop to finish
            }
          } catch (e) {
            console.error("Failed to parse SSE event:", trimmedLine, e);
          }
        }
      }
    } catch (error) {
      console.error('Execution Error:', error);
    } finally {
      setIsRunning(false);
    }
  }, [isRunning]);

  return { isRunning, executeWorkflow };
};
