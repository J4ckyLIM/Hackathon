import * as requestContext from 'request-context';

export class ContextService {
  private static readonly _nameSpace = 'request';

  public static get<T>(key: string): T {
    return requestContext.get(ContextService._getKeyWithNamespace(key));
  }

  public static set(key: string, value: any): void {
    requestContext.set(ContextService._getKeyWithNamespace(key), value);
  }

  private static _getKeyWithNamespace(key: string): string {
    return `${ContextService._nameSpace}.${key}`;
  }
}