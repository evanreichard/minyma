import re
import inspect
import os
import importlib.util

class MinymaPlugin:
    pass

class PluginLoader:
    def __init__(self):
        self.plugins = self.get_plugins()
        self.definitions = self.plugin_defs()


    def execute(self, func_cmd):
        print("[PluginLoader] Execute Function:", func_cmd)

        pattern = r'([a-z_]+)\('

        func_name_search = re.search(pattern, func_cmd)
        if not func_name_search:
            return

        func_name = func_name_search.group(1)

        # Not Safe
        if func_name in self.definitions:
            args = re.sub(pattern, '(', func_cmd)
            func = self.definitions[func_name]["func"]
            return eval("func%s" % args)


    def plugin_defs(self):
        defs = {}
        for plugin in self.plugins:
            plugin_name = plugin.name

            for func_obj in plugin.functions:
                func_name = func_obj.__name__
                function_name = "%s_%s" % (plugin_name, func_name)

                signature = inspect.signature(func_obj)
                params = list(
                    map(
                        lambda x: "%s: %s" % (x.name, x.annotation.__name__),
                        signature.parameters.values()
                    )
                )

                func_def = "%s(%s)" % (function_name, ", ".join(params))
                defs[function_name] = { "func": func_obj, "def": func_def }

        return defs

    def derive_function_definitions(self):
        """Dynamically generate function definitions"""
        function_definitions = []

        for plugin in self.plugins:
            plugin_name = plugin.name

            for method_obj in plugin.functions:
                method_name = method_obj.__name__
                signature = inspect.signature(method_obj)
                parameters = list(signature.parameters.values())

                # Extract Parameter Information
                params_info = {}
                for param in parameters:
                    param_name = param.name
                    param_type = param.annotation
                    params_info[param_name] = {"type": TYPE_DEFS[param_type]}

                # Store Function Information
                method_info = {
                    "name": "%s_%s" %(plugin_name, method_name),
                    "description": inspect.getdoc(method_obj),
                    "parameters": {
                        "type": "object",
                        "properties": params_info
                    }
                }
                function_definitions.append(method_info)

        return function_definitions


    def get_plugins(self):
        """Dynamically load plugins"""
        # Derive Plugin Folder
        loader_dir = os.path.dirname(os.path.abspath(__file__))
        plugin_folder = os.path.join(loader_dir, "plugins")

        # Find Minyma Plugins
        plugin_classes = []
        for filename in os.listdir(plugin_folder):

            # Exclude Files
            if not filename.endswith(".py") or filename == "__init__.py":
                continue

            # Derive Module Path
            module_name = os.path.splitext(filename)[0]
            module_path = os.path.join(plugin_folder, filename)

            # Load Module Dynamically
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None or spec.loader is None:
                raise ImportError("Unable to dynamically load plugin - %s" % filename)

            # Load & Exec Module
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Only Process MinymaPlugin SubClasses
            for _, member in inspect.getmembers(module):
                if inspect.isclass(member) and issubclass(member, MinymaPlugin) and member != MinymaPlugin:
                    plugin_classes.append(member)

        # Instantiate Plugins
        plugins = []
        for cls in plugin_classes:
            plugins.append(cls())
        return plugins
